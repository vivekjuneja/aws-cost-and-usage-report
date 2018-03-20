import smtplib
import settings


def send_email(team, to_email, start_date, end_date, cost):


	sent_from = settings.gmail_user  
	to = [to_email]  
	subject = "Your AWS expenses for last week is here"

	email_text = """\n
	Hello Team,\n
	This is an automated mail to inform you about the AWS cost for %s team from %s till %s.
	The AWS cost during the period is : %s Euros
	\nFor more information, please visit : https://console.aws.amazon.com/billing/home?region=eu-central-1#/costexplorer
	\n\nRemember 'Do More With Less' :)
	""" % (team, start_date, end_date, cost)

	message = 'Subject: {}\n\n{}'.format(subject, email_text)



	try:  
	    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	    server.ehlo()
	    server.login(settings.gmail_user, settings.gmail_password)
	    server.sendmail(sent_from, to, message)
	    server.close()

	    print('Email sent!')

	except Exception as e:  
	    print('Something went wrong...'+str(e))

