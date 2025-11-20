import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Test with SSL (port 465)
def test_ssl():
    print("Testing with SSL (port 465)...")
    try:
        msg = MIMEMultipart()
        msg['Subject'] = 'Test Email - SSL'
        msg['From'] = 'support@ttitanstocks.com'
        msg['To'] = 'peteresbull@gmail.com'
        msg.attach(MIMEText('This is a test email using SSL', 'plain'))
        
        with smtplib.SMTP_SSL('smtp.hostinger.com', 465, timeout=10) as server:
            server.set_debuglevel(1)
            server.login('support@ttitanstocks.com', '9eFy6NVBp@R')
            server.send_message(msg)
            print("✅ SSL Email sent successfully!")
            return True
    except Exception as e:
        print(f"❌ SSL Error: {e}")
        return False

# Test with TLS (port 587)
def test_tls():
    print("\nTesting with TLS (port 587)...")
    try:
        msg = MIMEMultipart()
        msg['Subject'] = 'Test Email - TLS'
        msg['From'] = 'support@ttitanstocks.com'
        msg['To'] = 'peteresbull@gmail.com'
        msg.attach(MIMEText('This is a test email using TLS', 'plain'))
        
        with smtplib.SMTP('smtp.hostinger.com', 587, timeout=10) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login('support@ttitanstocks.com', '9eFy6NVBp@R')
            server.send_message(msg)
            print("✅ TLS Email sent successfully!")
            return True
    except Exception as e:
        print(f"❌ TLS Error: {e}")
        return False

if __name__ == '__main__':
    ssl_success = test_ssl()
    tls_success = test_tls()
    
    print("\n" + "="*50)
    if ssl_success:
        print("✅ Use port 465 with SSL")
    elif tls_success:
        print("✅ Use port 587 with TLS")
    else:
        print("❌ Both methods failed. Check your credentials.")