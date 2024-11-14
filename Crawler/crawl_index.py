import requests
import pandas as pd
from datetime import datetime

url = 'https://finance.vietstock.vn/data/KQGDThongKeGiaStockPaging'
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': '_cc_id=ce2a8a9af12c25ef62ea562aea3dae6a; dable_uid=53044722.1710493651471; language=vi-VN; panoramaId_expiry=1731583626247; panoramaId=0598c25719d689992ff88c1edf2e16d5393841442e7aa21c6436e6cff5b2d12a; panoramaIdType=panoIndiv; Theme=Light; AnonymousNotification=; isShowLogin=true; ASP.NET_SessionId=syqi43kudrtmvg3w55pb20vu; __RequestVerificationToken=oNJsYbwv2IZJX7W5XlbKc7NysT92N8lQXuZmvBinS7PWw0kHlGvgSwo44cAzjvnnSVxErLrJKyRYgTQA_jKkd9viB6tL915Jj-jVkzdBE6I1; _gid=GA1.2.1745738540.1731569426; __gads=ID=903a4cbbe3ca3d50:T=1727447519:RT=1731569435:S=ALNI_MYFCdIm-lok4f-TW-oEcWT6TTe9LQ; __gpi=UID=00000f207bdbf994:T=1727447519:RT=1731569435:S=ALNI_MaMh_LC-Xx6e-M4IMV08vSXLimbSw; __eoi=ID=73503c8998817043:T=1727447519:RT=1731569435:S=AA-AfjaJCqHisvyIHcv8oKV2ekSp; finance_viewedstock=ACV,VCB,; vts_usr_lg=0F5988E5A9BAA11EF44F320EE70F3E59CD6D185BFA1DC04B7F778C777C3F5BD204295ABF46E750D08F1D2E70F3536BABEB1109208F94DEC757FBF07CD0E13AAD3865DD00A14F2596A7BBF389593F169B3DE9CDD85CC7F66BD068C08DE7ED795C435D62642A74EA15C9B4FFEE51D9480F8608259FFF81FC485ED52A7F5C74D407; vst_usr_lg_token=7gjga8OTokaEyfxu9LLosw==; _ga_EXMM0DKVEX=GS1.1.1731569424.14.1.1731569718.10.0.0; _ga=GA1.2.1647043453.1727447451; cto_bundle=wTMQu19rS3JUaXdNQVlKNFZnWDJrVkJlSjFEUDNucHdHMSUyRmdUM2h3MTNKYXc4ajRHNWtBRVR1U0JmOCUyRkptS3RtOGQ3cGpxc2xnVGhyaUlRaXdORGJqYTRoalVnRUhnMTVmVEJEMEJmbjVSc25BNVRUZzhQaTFac3B6Y01rU0ppNWp2dDhjRm1udHJUVk9oTElsZWExam5LWHlOdmJiN2NLcmtwaCUyQlFWUlVVVEUlMkJGVmkxcWpoMmdzUlQyNW1DWWo5WjFHUA; cto_bidid=aWT0j19wdWpMdmc3RGxmY05YSzZ0WXFnNlF4N2xmdFhwM3RERXdsakNYbkdURW9GaU5VOVhTU3VHaHF6MG1pdCUyRk8zTzZHWGg4NTlSSUxOeFhUMFFJRGNTRGwwTEpNVWl0MmJqRUpaUiUyQnl5VlBUWHdzNTFwamhmVTZvTXdpJTJGemp2VTlQZE11T3RlNEhtaWtab01nQ2ZINFpqVVElM0QlM0Q; cto_dna_bundle=V7f3pl9rS3JUaXdNQVlKNFZnWDJrVkJlSjFDTUdYTjFQdVFxUlQ0bHZpcXFVeDRteVQwWTJDaGNZZVBxWDlTZGExSWNTZmczV3dOdWJTYUh3QmZzQ2YwQXVXZyUzRCUzRA; cto_bundle=rUyApl9rS3JUaXdNQVlKNFZnWDJrVkJlSjFDQXpRaFRUZnFXdUJBNWVtY1F3RE9oNEwlMkJ4dzZzazQ2cmZQQUVSZ1hkSjgxemxzbHkyRzVGSGE5eEM3UHNMV01YdFE3T1JuMkVLT0ZIYmp3UHFLSlZxM3pZODFGeUQyWm1rYzhjaVpzdDIwcHlVJTJCY0ExUXBpMTNrTXEyYm9Wc25mZDkwU3R5MmtUOUVtZGpOVmIyaDJYNnlsdUw2QTY0YjY0dVMlMkI3Z0xaN3A',
    'Origin': 'https://finance.vietstock.vn',
    'Referer': 'https://finance.vietstock.vn/ket-qua-giao-dich',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}
base_data = {
    'page': '1',
    'pageSize': '20',
    'fromDate': '2022-10-14',
    'toDate': '2024-11-14',
    '__RequestVerificationToken': 'rVyx37ITw6hQwfsQvpO4hXz3meH5pFr8LTLDPh8tRhLCYYooaEH5u5KkgyaCFzImSZJY7xOQ-bhoCOgqyzXJQzQGORZhqqdEp8NRZsNXDPICO2hXg9ekQLIksNqChCnT0'
}

indices = {
    "VNIndex": (1, -19),
    "HNXIndex": (2, -18),
    "VN30Index": (4, -16),
    "HNX30Index": (5, -15),
    "UPCoMIndex": (3, -17)
}

def convert_date(date_str):
    timestamp = int(date_str.strip('/Date()')) / 1000
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')




for filename, (catID, stockID) in indices.items():
    page = 1
    all_data = pd.DataFrame()
    print(f"Processing {filename}...")

    while True:
        # Prepare data for the current request
        data = base_data.copy()
        data.update({
            'catID': str(catID),
            'stockID': str(stockID),
            'page': str(page)
        })

        # Send the POST request
        response = requests.post(url, headers=headers, data=data)
        
        # Check if the response is successful
        if response.status_code == 200:
            try:
                # Parse the JSON response
                response_data = response.json()
                
                # Remove the first element and retrieve the trading data
                trading_data = response_data[1]
                
                # Break the loop if there's no data on this page
                if not trading_data:
                    break
                
                # Convert the data to a DataFrame
                df = pd.DataFrame(trading_data)
                
                # Apply the conversion function to the TradingDate column
                df['TradingDate'] = df['TradingDate'].apply(convert_date)
                
                # Append the page data to the all_data DataFrame
                all_data = pd.concat([all_data, df], ignore_index=True)
                
                # Increment the page number
                page += 1
            except ValueError:
                # If JSON decoding fails, print the raw response text for debugging
                print(f"JSON decode error on {filename} page {page}. Response text:\n{response.text}")
                break
        else:
            print(f"Failed to retrieve data for {filename} on page {page} with status code:", response.status_code)
            break

    # Save the DataFrame for each index to its respective CSV file
    all_data.to_csv(f"{filename}.csv", index=False, encoding="utf-8")
    print(f"Data for {filename} saved to {filename}.csv")