from django.shortcuts import render, HttpResponse
from django.http import HttpResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import threading


# Background email sending function
def send_email_async(msg, user_email, app_password):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user_email, app_password)
        server.send_message(msg)
        server.quit()
        print(" Email sent successfully in background.")
    except Exception as e:
        print(f" Failed to send email: {e}")


def send_email(request):
    if request.method == "POST":
        name = request.POST["name"]
        user_email = request.POST["email"]
        app_password = request.POST["app_password"]
        to_email = request.POST["to_email"]
        subject = request.POST["subject"]
        message = request.POST["message"]
        file = request.FILES.get("attachment")
        logo = request.FILES.get("logo")

        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

        if file and file.size > MAX_FILE_SIZE:
            return render(request, "index.html", {"error": " Attachment too large (Max 2MB allowed)"})

        if logo and logo.size > MAX_FILE_SIZE:
            return render(request, "index.html", {"error": " Logo too large (Max 2MB allowed)"})

        # Email HTML body

        html_body = f"""
<html>
<head>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #f5f5f5;
    }}
    .email-wrapper {{
      background-color: #fff;
      padding: 0;
      margin: 20px auto;
      max-width: 600px;
      border-radius: 10px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.1);
      overflow: hidden;
      text-align: center;
    }}
    .banner-logo {{
      width: 100%;
      max-height: 200px;
      object-fit: cover;
      display: block;
    }}
    .content {{
      padding: 20px;
    }}
    .greeting {{
      font-size: 24px;
      color: #2c3e50;
      margin-bottom: 10px;
    }}
    .message {{
      font-size: 16px;
      line-height: 1.6;
      color: #333;
      margin-bottom: 20px;
    }}
    .sent-time {{
      font-size: 14px;
      color: #777;
      margin-bottom: 20px;
    }}
    .reply-btn {{
      background-color: #4e9bff;
      color: white;
      padding: 10px 18px;
      text-decoration: none;
      border-radius: 6px;
      display: inline-block;
      margin-bottom: 20px;
    }}
    .social-icons img {{
      width: 30px;
      margin: 0 8px;
    }}
    .footer {{
      font-size: 13px;
      color: #999;
      margin-top: 25px;
      padding-bottom: 20px;
    }}

    /* Dark Mode */
    @media (prefers-color-scheme: dark) {{
      body {{
        background-color: #1e1e1e;
      }}
      .email-wrapper {{
        background-color: #2c2c2c;
        color: #eee;
      }}
      .message, .sent-time {{
        color: #ccc;
      }}
      .reply-btn {{
        background-color: #6ea8fe;
      }}
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">
    {'<img src="cid:logo" class="banner-logo" alt="Logo">' if logo else ''}
    <div class="content">
      <h2 class="greeting">Hi, I'm {name}</h2>
      <p class="message">{message}</p>
      <a href="mailto:{user_email}" class="reply-btn">Reply to {name}</a>

      <div class="social-icons">
        <a href="https://github.com/Ishtiaq-Codes"><img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" alt="GitHub"></a>
      </div>

      <div class="footer">
        Sent via Django Email Sender • Built by Ishtiaq-Codes 
      </div>
    </div>
  </div>
</body>
</html>
"""




        #  email
        msg = MIMEMultipart()
        msg["From"] = user_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        
        if logo:
            logo_data = logo.read()
            image_subtype = logo.content_type.split('/')[1]
            image = MIMEImage(logo_data, _subtype=image_subtype)
            image.add_header("Content-ID", "<logo>")
            image.add_header("Content-Disposition", "inline")
            image.add_header("X-Attachment-Id", "logo")
            msg.attach(image)

       
        if file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{file.name}"')
            msg.attach(part)

        # email sending in a separate thread
        threading.Thread(target=send_email_async, args=(msg, user_email, app_password)).start()

        
        return render(request, "index.html", {"message": "✅ Email sent successfully..."})

    return render(request, "index.html")


def home(request):
    return HttpResponse("Welcome to World War 0.....joke")
