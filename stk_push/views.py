import requests
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Transaction
import base64
from datetime import datetime
import json


class MpesaPassword:
    @staticmethod
    def generate_security_credential():
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Safaricom credentials
        business_short_code = '174379'  # Your shortcode here
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  
        data_to_encode = business_short_code + passkey + timestamp
        online_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

        return online_password


# Safaricom daraja credentials
CONSUMER_KEY = 'jkXBgjW27IKhblgEVsR5SOfTh6Am0MZ3IWs1xTPIyKgLA70x'  
CONSUMER_SECRET = 'z6WM04Fv88SyG8QeSgtva1GXdNyWPpbOi6vTNuEbuA6aL64l6sqAzxqpePAEXYvG'  
SHORTCODE = '174379'  
PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  
BASE_URL = 'https://sandbox.safaricom.co.ke'  

def generate_access_token():
    auth_url = f'{BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get('access_token')


def query_transaction(transaction_id):
    access_token = generate_access_token()
    status_url = f'{BASE_URL}/mpesa/transactionstatus/v1/query'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    security_credential = MpesaPassword.generate_security_credential()

    payload = {
        "Initiator": 'testapi',  
        "SecurityCredential": security_credential,  
        "CommandID": "TransactionStatusQuery",
        "TransactionID": transaction_id,
        "PartyA": SHORTCODE,
        "IdentifierType": "1", 
        "ResultURL": "https://1515-2c0f-fe38-2327-df6a-d8b9-fba7-b3c8-9e80.ngrok-free.app/callback/transaction_status/",
        "QueueTimeOutURL": "https://1515-2c0f-fe38-2327-df6a-d8b9-fba7-b3c8-9e80.ngrok-free.app/callback/transaction_timeout/",
        "Remarks": "Checking transaction status",
        "Occasion": "STK Push"
    }

    response = requests.post(status_url, json=payload, headers=headers)
    return response.json()


def index(request):
    return render(request, 'index.html')


@csrf_exempt

def stk_push(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')  
        amount = request.POST.get('amount')  

     
        transaction = Transaction.objects.create(
            phone_number=phone,
            amount=amount,
            status="Pending",
            description="Awaiting callback",
        )

        access_token = generate_access_token()
        stk_url = f'{BASE_URL}/mpesa/stkpush/v1/processrequest'
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  
        

        password = base64.b64encode(f'{SHORTCODE}{PASSKEY}{timestamp}'.encode()).decode()

        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,  
            "PartyB": SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": "https://1515-2c0f-fe38-2327-df6a-d8b9-fba7-b3c8-9e80.ngrok-free.app/callback/", 
            "AccountReference": f"Transaction_{transaction.id}",
            "TransactionDesc": "Payment for services"
        }

        response = requests.post(stk_url, json=payload, headers=headers)
        response_data = response.json()
        transaction_id = response_data.get('CheckoutRequestID', None)
        transaction.transaction_id = transaction_id
        transaction.description = response_data.get('ResponseDescription', 'No description')
        transaction.save()

    
        return redirect('waiting_page', transaction_id=transaction.id)

    return JsonResponse({"error": "Invalid request"}, status=400)


# @csrf_exempt
# def callback(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         print("Received callback data:", data)  # For debugging

#         stk_callback = data.get('Body', {}).get('stkCallback', {})
#         result_code = stk_callback.get('ResultCode', None)  # Get the result code
#         result_desc = stk_callback.get('ResultDesc', '')  # Get the result description
#         transaction_id = stk_callback.get('CheckoutRequestID', None)

#         print(f"Transaction ID: {transaction_id}, Result Code: {result_code}, Result Description: {result_desc}")

#         # If transaction_id exists, find the transaction and update it
#         if transaction_id:
#             transaction = Transaction.objects.filter(transaction_id=transaction_id).first()

#             if transaction:
#                 if result_code == 0:  # Transaction successful
#                     callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
#                     receipt_number = next((item['Value'] for item in callback_metadata if item['Name'] == 'MpesaReceiptNumber'), None)
#                     amount = next((item['Value'] for item in callback_metadata if item['Name'] == 'Amount'), None)
#                     transaction_date_str = next((item['Value'] for item in callback_metadata if item['Name'] == 'TransactionDate'), None)

#                     transaction_date = None
#                     if transaction_date_str:
#                         transaction_date = datetime.strptime(str(transaction_date_str), "%Y%m%d%H%M%S")

#                     # Update the transaction to reflect success
#                     transaction.mpesa_receipt_number = receipt_number
#                     transaction.transaction_date = transaction_date
#                     transaction.amount = amount
#                     transaction.status = "Success"
#                     transaction.description = "Payment successful"
#                     transaction.save()

#                     print("Transaction updated successfully.")

#                 elif result_code == 1:  # Failed transaction
#                     transaction.status = "Failed"
#                     transaction.description = result_desc or "Payment failed due to an error."
#                     transaction.save()

#                     print(f"Transaction failed: {result_desc or 'No description provided.'}")

#                 elif result_code == 1032:  # Cancelled transaction
#                     transaction.status = "Cancelled"
#                     transaction.description = result_desc or "Transaction was cancelled by the user."
#                     transaction.save()

#                     print(f"Transaction cancelled: {result_desc or 'No description provided.'}")

#                 else:
#                     transaction.status = "Unknown"
#                     transaction.description = f"Unhandled result code: {result_code}. {result_desc}"
#                     transaction.save()

#                     print(f"Unhandled result code: {result_code}, Description: {result_desc}")

#         return JsonResponse({"message": "Callback received and processed"}, status=200)

#     return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Received callback data:", data) 

        stk_callback = data.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode', None)  
        result_desc = stk_callback.get('ResultDesc', '')  
        transaction_id = stk_callback.get('CheckoutRequestID', None)

        print(f"Transaction ID: {transaction_id}, Result Code: {result_code}, Result Description: {result_desc}")

  
        if transaction_id:
            transaction = Transaction.objects.filter(transaction_id=transaction_id).first()

            if transaction:
                if result_code == 0:  
                    callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    receipt_number = next((item['Value'] for item in callback_metadata if item['Name'] == 'MpesaReceiptNumber'), None)
                    amount = next((item['Value'] for item in callback_metadata if item['Name'] == 'Amount'), None)
                    transaction_date_str = next((item['Value'] for item in callback_metadata if item['Name'] == 'TransactionDate'), None)

                    transaction_date = None
                    if transaction_date_str:
                        transaction_date = datetime.strptime(str(transaction_date_str), "%Y%m%d%H%M%S")

                    transaction.mpesa_receipt_number = receipt_number
                    transaction.transaction_date = transaction_date
                    transaction.amount = amount
                    transaction.status = "Success"
                    transaction.description = "Payment successful"
                    transaction.save()

                    print("Transaction updated successfully.")

                elif result_code == 1:  
                    transaction.status = "Failed"
                    transaction.description = result_desc  
                    transaction.save()

                    print(f"Transaction failed: {result_desc}")

                elif result_code == 2: 
                    transaction.status = "Cancelled"
                    transaction.description = "Transaction was cancelled by the user"
                    transaction.save()

                    print(f"Transaction cancelled: {result_desc}")

        return JsonResponse({"message": "Callback received and processed"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)



def waiting_page(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    return render(request, 'waiting.html', {'transaction_id': transaction_id})


def check_status(request, transaction_id):
    transaction = Transaction.objects.filter(id=transaction_id).first()

    if not transaction:
        return JsonResponse({"status": "Failed", "message": "Transaction not found"}, status=404)

    if transaction.status == "Success":
        return JsonResponse({"status": "Success", "message": "Payment Successful"})
    elif transaction.status == "Failed":
        return JsonResponse({"status": "Failed", "message": "Payment Failed"})
    elif transaction.status == "Cancelled":
        return JsonResponse({"status": "Cancelled", "message": "Transaction was cancelled by the user"})
    else:
        return JsonResponse({"status": "Unknown", "message": "Transaction is still being processed or status is unknown"})


def payment_success(request):
    return render(request, 'payment_success.html')



def payment_failed(request):
    return render(request, 'payment_failed.html')


def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')