# budget_automation_tool

Greetings, fellow living being,

This project started as an extension of a habit I had of tracking my expenses in an Excel sheet (as destiny mandates), and the fact that, albeit a reflecting exercise, it was too manually upload my expenses. It eventually became a tedious task. Therefore, in this project, I look forward to:
1. Automating the expenses tracking process by extracting the emails sent by banks and putting them all in a dataframe.
2. Matching said expenses to the fictional budget created and returning a difference every time a transaction is made.
3. Finally, sending a message to the messaging app of preference (WhatsApp will be used for this project) and in said message establishing the remaining budget amounts for each category to make the user aware of the available amounts left for the current month.

Disclaimer: all expenses and transactions for this project are fictional and have been fabricated for scientific purposes.

Results as of January 29th, 2024.
Transformed extracted emails into a dataframe.
<img width="1352" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/df17a8aa-a0b2-4d42-ae9c-33597634abd5">

February 05th, 2024.
After some work during the weekend, the following was done:
Creation of lists: one with the current 2024 budget, and a list per category of expenses.
After that, I created a new column in my expenses_df categorizing each expense row. This was done by adding keywords to each category list and finding that keyword in the Establishment name row (Comercio).

Additionally, I modified the date to exclude the time and only add YYYY-MM in a new column called 'Date'. This way I can use this same column for filtering later. The objective is for this to be a variable that refreshes itself every time a month begins so that no changes have to be done to the code date-wise. This last bit is accomplished through the variable current_month.

<img width="1014" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/08a144aa-3daa-4251-a774-4f7edef4cb3a">
<img width="1014" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/0201b4bd-9b90-4b26-9a37-f34fcf13d7ca">

It is worth noting that, as can be seen above. Out of the almost 100 mails extracted, the two regex patterns currently used seem to be leaving out 7 emails, which is something that I must look into later. Why are these emails with no match if all emails are supposed to have the same formatting? Must inquire.

Furthermore, I used pandas to group and sum expenses by category, also filtering expenses by the date variable discussed earlier, current_month, which as it explicitly implies, carries out only the expenses for the current month, which is FEB2024 (2024-02 in the code format) as of today.

![image](https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/114d6896-3c4b-446d-9347-f9b7d9b760d9)

After the grouping has been done, a for loop is created with the variable category to go through the expenses_df column 'Category' and match it to each one of them, later on doing the same in a nested loop for the dates. A difference of the budget_2024 list and the filtered_expenses is done to obtain the current remaining amount for each category. As it can be seen in the following image. There is a hefty amount of prints and dataframe structures throughout this file and the code, and that is because I was using said print statements for debugging. However, after further cleaning of the code, it should all look neater. Until then, this is the progress so far:

![image](https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/fd2d6200-6734-4f1f-8a93-1f249a54ae43)

Moreover, the only categories that have been matched so far have been Eating Out and Subscriptions. The final two dataframes look as follows:
![image](https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/243f82c2-7834-4315-ad28-8667b42cc345)


February 11th. 2024.
In these past few days I've encountered several new issues and solutions. I will briefly summarize them here:
1. Change of email address selection method
   I went from having a single key and value with my_mail.search() method to creating a list with the desired addresses to receive emails from and then running a for loop through, it only appending mails to a newly created empty list, called search_results_list, if the status of the method was 'OK'. This allows the versatility of having as many senders as desired with only having to include them in email_addresses_to_extract. 
2. Creation of counts to monitor the type of data being handled and debug. Had four categorie that included the following:
   <img width="498" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/2b8c3c50-5684-4fd0-bf52-64e31daad4b1">
3. Learnt to use try: and except: to find and handle anormalities. Scotiabank sends several types of mails through the same sender which had the code return errors constantly, given that we only wanted to extract credit cards statements. So monthly statements, payments to the credit card and other type of emails began posing error problems.
4. Change of data extraction from mails block 2.1. given that the change of method in block 1.3. made this block return Nones in the data extraction part of each message. Block 2.1. includes data extraction from emails and extraction of senders information (SENDER and SUBJECT). It is worth noting that the sender's information has to be extracted in this manner now because the new method was not giving a compatible output with the 'RFC822' standard.
   <img width="960" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/6b846135-5bcf-43c9-ae2d-510899af027e">
5. The extraction of the header became an issue because it was completelly illegible. Decoding it to base64 was the answer.
  Subject Decoding:Used email.header.decode_header to decode the subject.
  If the subject is encoded in base64, decoded it using base64.b64decode.
  Checked for the subject's type (bytes) and decoded accordingly.
7. Store Name, USD Amount and Date Extraction:
  Used regular expressions to extract store names, USD amounts, and transaction dates.
  Applied specific patterns to match the desired information in the email body.
8. Used re.search to find matches in the body. I still have a pending of making Scotiabanks regex pattern more robust. CURENT ISSUE, not all names are taken in properly. If there’s special characters in/after the name, it is cut out, for example: The Grove in SFO whose name is ‘TST* The Grove - Yerba Bu’ is cut out only TST, which will not give enough context when reading the final results.
9. For the transaction date, removed extra characters and applied strip() before converting to datetime.
  Stripping Extra Spaces in Date:
  Applied strip() directly when converting the string to datetime to remove any leading or trailing spaces.
10. Removed undesired email types. I.e: bank statements and credit card payments. These amount to about 10% of all Scotiabank emails.
    Current email count:
    <img width="960" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/95ef9da3-1ee0-4a9d-9e29-784636e122f7">
11. Verified accuracy of BAC data extraction. No issues were found. Proceed to comment all debuging printing statements.
12. Verified accurady of Scotiabank data extraction. Issues found:
    Must take emails that are not credit card expenses out of the equation.
    Email count before this issue is addressed:
    <img width="960" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/59eccd27-555b-46e0-a256-25c63be9ec14">
    Once a regex pattern is applied to match along with the senders address for scotiabank. Our email count is updated to:
    <img width="960" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/4048cbf4-9fb2-42fb-ad03-f8f2dfd615b6">
    Thus reducing undesired emails to 0.

This way, our code's output is updated to
  <img width="960" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/c3c94cd1-e4ef-4fb0-b942-5ce0b9a941c7">

13. Transforming Bank Dictionaries into DataFrames: Transformed both bank dictionaries of expenses into dataframes.
  <img width="960" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/bebb119a-9791-4d90-a77b-04861475ed8c">

It is through this that I see a disparity in the total amount of rows in the dataframe and the amount of emails totaled in the count below.
Upon further inspection, two issues arise:
1. Unmatched BAC emails due to a lack of matching in the USD amount (in Colombian Pesos).
   <img width="960" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/cb0350c8-919b-4fe4-8b71-160caa979e1d">
2. Mismatch in Scotiabank's emails due to establishment names beginning with numbers.
   <img width="1351" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/8c8649eb-20dc-46dc-b06a-669198f61db2">

   Disparity in Total Rows and Email Count:
Identified two issues:

Next Steps:

Address regex pattern issues for both banks to include other currencies.
Make establishment name collection more flexible to allow names beginning with numbers.
This journey continues...


February 12th, 2024.
Today was a great day for debugging and deepening knowledge about filtering, loc, and the legendary 'SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame' that pops up when slicing through a view instead of the main DataFrame in pandas. 

1. Added the new category column
2. Transformed the 'Transaction Date' column to datetime to sort dates in descending order, dtype was object previously.
3. Added additional keywords to make the category lists more robust. By including all expense emails from Scotiabank, many 'Uncategorized' rows came up. 
4. Defined the function to categorize said expenses automatically.
5. Created 'current month' variable to filter expenses for the ongoing month.
6. Created a new column 'Transaction Month' to effectively group later.
7. Grouped and summed expenses for the current month by 'Category' and 'Transaction Month'.
8. Created a copy of the DataFrame 'current_month_expenses_df' to make sure changes were not done on the original to debug for 'SettingWithCopyWarning'.

Current output:
<img width="1014" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/f0b026b7-2248-45db-8cc3-c3b120a378c7">

Since February 14th, 2024.
1. Explored posibilities of automating with AWS Lambda funcions. Through exploration, it is safe to conclude that although a useful too, it is a hammer too big for the nail. In other words, a simpler tool will do, that's why I resorted to a CRONJOB.
2. Larned how to set cronjobs through the nano editor to create a cron_log.
3. Fixed issues with library dependencies in Pycharm by working with Anaconda and its package manager Condas. 
4. Created a shell script file to ease the creation and management of the cronjob.
Output:
<img width="1014" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/8c9c78ec-5c57-4907-ac0e-3fb84e01623d">
5. Transformed last remaining balances dictionary into a dataframe to have the last bit of code to show as:
<img width="1014" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/31b47e64-8d1c-487f-b4c2-ba91d00e5f4c">

