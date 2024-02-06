# budget_automation_tool

Greetings, fellow living being,

This project started as an extension of a habit I had of tracking my expenses in an Excel sheet (as destiny mandates) and the fact that albeit a reflecting excersice it was to manually upload my expeses, it eventually became a tedious task. Therefore, in this project I look forward to: 
1. Automating the expenses tracking process by extracting the emails sent by banks and putting them all in a dataframe.
2. Matching said expenses to the ficitonal budget created and returning a difference everytime a transaction is made.
3. Finally,sending a message to the messaging app of preference (Whatsapp will be used for this project) and it said message establishing the remaining budget amounts for each category to make the user aware of the available amounts left for the current month.

Disclaimer: all expenses and transactions for this project are fictional and have been fabricated for scientific purposes. 

Results as of January 29th, 2024. 
Transformed extracted emails into a dataframe.
<img width="1352" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/df17a8aa-a0b2-4d42-ae9c-33597634abd5">

February 05th, 2024.
After some work during the weekend, the following was done:
Creation of lists: one with the current 2024 budget, and a list per category of expenses. 
After that, I created a new column in my expenses_df categorized each expense row. This was done by adding keywords to each category list and finding that keyword in the Establishment name row (Comercio). 

Addidionally, I modified the date to exclude the time and only add YYYY-MM in a new columnd called 'Date'. This way I can use this same column for filtering later. The objective is for this to be a variable that refreshed itself everytime a month begins, so that no changes have to be done to the code date-wise. This last bit is accomplished through the variable current_month.

![image](https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/7a114682-4aa1-4347-8748-78d6bd2a88ba)

It is worth noting that, as it can be seen above. Out of the almost 100 mails extracted, the two regex patterns currently used seem to be leaving out 7 emails, which is something that I must look into later. Why are they emails with no match if all emails are supposed to have the same formatting? Must inquire.

Furthermore, I used pandas to group and sum expenses by category, also filtering expenses by the date variable discussed earlier, current_month, which as it explicitly implies, carries out only the expenses for the current month which is FEB2024 (2024-02 in the code format) as of today.

![image](https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/114d6896-3c4b-446d-9347-f9b7d9b760d9)

After the grouping has been done, a for loop is created with variable category to go through the expenses_df column 'Category' and match it to each one of then, later on doing the same in a nested loop for the dates. A difference of the budget_2024 list and the filtered_expenses is done to obtain the current remaining amount for each category. As it can be seen in the following image. There is a hefty amount of prints and dataframe structures throughout this file and the code and that is because I was using said print statements for debugging. However, after further cleaning of the code, it should all look neater. Until then, this is the progress so far: 

![image](https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/fd2d6200-6734-4f1f-8a93-1f249a54ae43)

Moreover,the only categories that have been matched so far have been Eating Out and Subscriptions. The final two dataframes look as follows: 

![image](https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/243f82c2-7834-4315-ad28-8667b42cc345)
