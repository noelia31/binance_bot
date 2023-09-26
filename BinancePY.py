#!/usr/bin/env python
# coding: utf-8

# In[88]:


#pip install slack-sdk


# In[165]:


def get_crypto_data(currency):
    # Define the API URL and payload based on the currency
    api = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    
    if currency == 'USD':
        payload = {
            "asset": "USDT",
            "countries": [],
            "fiat": "USD",
            "page": 1,
            "payTypes": ["Wise"],
            "proMerchantAds": False,
            "publisherType": None,
            "rows": 10,
            "tradeType": "BUY"
        }
    elif currency == 'BOB':
        payload = {
            "asset": "USDT",
            "countries": [],
            "fiat": "BOB",
            "page": 1,
            "payTypes": [],
            "proMerchantAds": False,
            "publisherType": None,
            "rows": 10,
            "tradeType": "SELL"
        }
    else:
        raise ValueError("Invalid currency. Supported currencies: 'USD' and 'BOB'")
    
    # Request data from the API
    data = requests.post(api, json=payload).json()
    
    # Process the retrieved data into a DataFrame
    all_data = []
    for d in data['data']:
        all_data.append({
            'name': d['advertiser']['nickName'],
            'orders': d['advertiser']['monthOrderCount'],
            'rate': d['advertiser']['monthFinishRate'],
            'user_type': d['advertiser']['userType'],
            'price': d['adv']['price'],
            'MinAmount': d['adv']['minSingleTransAmount'],
            'MaxAmount': d['adv']['maxSingleTransAmount']
        })
    
    df = pd.DataFrame(all_data)
    df['price'] = df['price'].astype(float)
    
    return df


# In[171]:


from slack_sdk import WebClient

def send_slack_message(token, channel_id, message_dict):
    """
    Sends a message to a Slack channel using a dictionary as the message.

    :param token: The authentication token of your Slack application.
    :param channel_id: The ID of the channel where you want to send the message.
    :param message_dict: A dictionary containing the message. It should have the format {"text": "Message text"}.
    :return: True if the message was sent successfully, False otherwise.
    """
    # Replace 'YOUR_TOKEN' with your Slack application's authentication token
    slack_token = 'xoxb-5947849624978-5947928994274-nS5UiAPWc2oGJheQxptjLkm6'

    # ID of the channel you want to send the message to (you can find it in the channel's URL)
    channel_id = 'C05TFAVGBB9'
    
    try:
        # Create a WebClient object with the provided token
        client = WebClient(token=token)
        
        message = "Esos son los vendedores disponibles \n"
        # Format the dictionary as a string with titles in bold, newline characters, and no quotes
        
        for seller_info in message_dict:
            message += "\n---------------------------\n"
            for key, value in seller_info.items():
                message += f"{key}: {value}\n"
        
        # Use the chat_postMessage function to send the message to the channel
        response = client.chat_postMessage(
            channel=channel_id,
            text=message
        )

        # Check if the message was sent successfully
        if response["ok"]:
            print("Message sent successfully")
            return True
        else:
            print("Error sending the message:", response["error"])
            return False

    except Exception as e:
        print("Error sending the message:", str(e))
        return False


# In[172]:


def process_and_send_data(value, currency):
    # Check if currency is 'USD' or 'BOB' and set the condition accordingly
    if currency == 'USD':
        df= get_crypto_data('USD')
        condition = df["price"] <= value
    elif currency == 'BOB':
        df= get_crypto_data('BOB')
        condition = df["price"] >= value
    else:
        raise ValueError("Invalid currency. Supported currencies: 'USD' and 'BOB'")
    
    # Filter the records based on the condition
    filtered_df = df[condition].head(3)
    
    # Check if at least one record meets the condition
    if not filtered_df.empty:        
        # Convert the records to a list of dictionaries
        records_as_list = filtered_df.to_dict(orient='records')
        # Send the records to the Slack channel
        successfully_sent = send_slack_message(token, channel_id, records_as_list)
        return successfully_sent
    else:
        print("No record meets the condition for currency", currency)
        return False


# In[173]:


usd_min_value = 1.015
bob_max_value = 7.20

# Llamar a la función para procesar y enviar datos en USD
usd_success = process_and_send_data(usd_min_value,'USD')
if usd_success:
    print("Datos en USD procesados y enviados con éxito.")
else:
    print("No se enviaron datos en USD.")

# Llamar a la función para procesar y enviar datos en BOB
bob_success = process_and_send_data(bob_max_value,'BOB')
if bob_success:
    print("Datos en BOB procesados y enviados con éxito.")
else:
    print("No se enviaron datos en BOB.")


# In[ ]:




