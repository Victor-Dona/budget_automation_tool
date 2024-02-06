# budget_automation_tool

Results as of January 29th. Transformed extracted emails into a dataframe.
<img width="1352" alt="image" src="https://github.com/Victor-Dona/budget_automation_tool/assets/158128371/df17a8aa-a0b2-4d42-ae9c-33597634abd5">

After some work during the weekend, the following was done:
Creation of lists: one with the current 2024 budget, and a list per category of expenses. 
After that, I created a new column in my expenses_df categorized each expense row. This was done by adding keywords to each category list and finding that keyword in the Establishment name row (Comercio). 

Addidionally, I modified the date to exclude the time and only add YYYY-MM in a new columnd called 'Date'. This way I can use this same column for filtering later. The objective is for this to be a variable that refreshed itself everytime a month begins, so that no changes have to be done to the code date-wise. This last bit is accomplished through the variable current_month.


