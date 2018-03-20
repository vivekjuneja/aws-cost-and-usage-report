#!/usr/bin/env python3

import argparse
import boto3
import datetime
import gmail
import settings

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

now = datetime.datetime.utcnow()
parser = argparse.ArgumentParser()
parser.add_argument('--days', type=int, default=30)
parser.add_argument('--start', type=str, default=(now - datetime.timedelta(2)).strftime('%Y-%m-%d'))
parser.add_argument('--end', type=str, default=now.strftime('%Y-%m-%d'))

args = parser.parse_args()


#now = datetime.datetime.utcnow()
#start = (now - datetime.timedelta(days=args.days)).strftime('%Y-%m-%d')
#end = now.strftime('%Y-%m-%d')
end = (datetime.datetime.strptime(args.end, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
start = args.start

print('start date : ', start)
print('end date : ', end)

def calculate_cost(team, to_email):
    cd = boto3.client('ce', aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY[team], aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY[team], region_name='us-east-1' )

    results = []

    token = None
    while True:
        if token:
            kwargs = {'NextPageToken': token}
        else:
            kwargs = {}
        data = cd.get_cost_and_usage(TimePeriod={'Start': start, 'End':  end}, Granularity='DAILY', Metrics=['UnblendedCost'], GroupBy=[{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}, {'Type': 'DIMENSION', 'Key': 'SERVICE'}], **kwargs)
        results += data['ResultsByTime']
        token = data.get('NextPageToken')
        if not token:
            break

    print('\t'.join(['TimePeriod', 'LinkedAccount', 'Service', 'Amount', 'Unit', 'Estimated']))

    total_cost = 0
    for result_by_time in results:
        for group in result_by_time['Groups']:
            amount = group['Metrics']['UnblendedCost']['Amount']
            total_cost += float(amount)
            unit = group['Metrics']['UnblendedCost']['Unit']
            print(result_by_time['TimePeriod']['Start'], '\t', '\t'.join(group['Keys']), '\t', amount, '\t', unit, '\t', result_by_time['Estimated'])

    rounded_total_cost = round(total_cost, 2)
    print('Total Cost ' + str(rounded_total_cost))
    
    gmail.send_email(team, to_email, start, args.end, rounded_total_cost)


for team, email in settings.teams.items():
    calculate_cost(team, email)
