from flask import Flask, request, render_template
import datetime
import numpy as np
import numpy_financial as npf  # Import numpy_financial

app = Flask(__name__)

# Function to calculate DATEDIF
def datedif(start_date, end_date, unit):
    start_date = datetime.datetime.strptime(start_date, "%B/%Y")
    end_date = datetime.datetime.strptime(end_date, "%B/%Y")
    delta = end_date - start_date
    if unit == "m":
        return delta.days // 30

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect inputs from form data
        data = request.form

        # Helper function to clean and convert numbers
        def clean_number(value):
            return float(value.replace(',', '').strip())

        # Collect inputs
        applying_as_student_nsf = data.get('applying_as_student_nsf')
        price_of_house = clean_number(data.get('price_of_house'))
        house_completion_month = data.get('house_completion_month')
        house_completion_year = data.get('house_completion_year')
        house_completion_date = f"{house_completion_month}/{house_completion_year}"
        room_type = data.get('room_type')
        plh = data.get('plh')
        plh_percentage = float(data.get('plh_percentage') or 0)
        husband_oa_cpf_value = clean_number(data.get('husband_oa_cpf_value'))
        wife_oa_cpf_value = clean_number(data.get('wife_oa_cpf_value'))
        husband_start_work_month = data.get('husband_start_work_month')
        husband_start_work_year = data.get('husband_start_work_year')
        husband_start_work_date = f"{husband_start_work_month}/{husband_start_work_year}"
        wife_start_work_month = data.get('wife_start_work_month')
        wife_start_work_year = data.get('wife_start_work_year')
        wife_start_work_date = f"{wife_start_work_month}/{wife_start_work_year}"
        husband_salary = clean_number(data.get('husband_salary'))
        wife_salary = clean_number(data.get('wife_salary'))
        estimated_renovation_fee = clean_number(data.get('estimated_renovation_fee'))

        # Constants
        current_date = "June/2024"
        cpf_contribution_rate = 0.37 * 0.6217

        # Calculations
        husband_monthly_cpf_oa = cpf_contribution_rate * husband_salary
        wife_monthly_cpf_oa = cpf_contribution_rate * wife_salary

        amount_cpf_husband_to_key_collection = datedif(husband_start_work_date, current_date, "m") * husband_monthly_cpf_oa
        amount_cpf_wife_to_key_collection = datedif(wife_start_work_date, current_date, "m") * wife_monthly_cpf_oa

        # Grants
        income_sum = husband_salary + wife_salary

        # Enhanced CPF Grant lookup table
        income_brackets = np.array([0, 1501, 2001, 2501, 3001, 3501, 4001, 4501, 5001, 5501, 6001, 6501, 7001, 7501, 8001, 8501, 9001])
        cpf_grants = np.array([80000, 75000, 70000, 65000, 60000, 55000, 50000, 45000, 40000, 35000, 30000, 25000, 20000, 15000, 10000, 5000, 0])
        enhanced_cpf_grant = cpf_grants[np.searchsorted(income_brackets, income_sum, side="right") - 1]

        plh_grant = plh_percentage * price_of_house if plh == "YES" else 0
        final_price_of_house = price_of_house - (enhanced_cpf_grant + plh_grant)

        # Payments
        # ~0.5 Year after BTO Ballot
        option_fee = 1000 if room_type == "3 ROOM" else 2000

        # ~1 Year after BTO Ballot
        total_oa_cpf_value = husband_oa_cpf_value + wife_oa_cpf_value
        if applying_as_student_nsf == "YES":
            first_downpayment = 0.025 * final_price_of_house - total_oa_cpf_value
        else:
            first_downpayment = 0.05 * final_price_of_house - total_oa_cpf_value

        # Ensure first_downpayment is not negative
        first_downpayment = max(first_downpayment, 0)

        # Stamp Duty Calculation
        if final_price_of_house <= 180000:
            stamp_duty = 0.01 * final_price_of_house
        elif final_price_of_house <= 360000:
            stamp_duty = 180000 * 0.01 + (final_price_of_house - 180000) * 0.02
        elif final_price_of_house <= 1000000:
            stamp_duty = 180000 * 0.01 + 180000 * 0.02 + (final_price_of_house - 360000) * 0.03
        else:
            stamp_duty = 180000 * 0.01 + 180000 * 0.02 + 640000 * 0.03 + (final_price_of_house - 1000000) * 0.04

        total_first_payment = first_downpayment + stamp_duty

        # Key Collection Day!
        total_amount_cpf_to_key_collection = amount_cpf_husband_to_key_collection + amount_cpf_wife_to_key_collection
        second_downpayment = 0.2 * final_price_of_house - option_fee - total_amount_cpf_to_key_collection

        # Ensure second_downpayment is not negative
        second_downpayment = max(second_downpayment, 0)

        renovation_fee = estimated_renovation_fee
        lease_in_escrow = 38.30
        if room_type == "4 ROOM":
            survey_fees = 297
        elif room_type == "3 ROOM":
            survey_fees = 229.5
        else:
            survey_fees = 351

        stamp_duty_deed_assignment = min(0.004 * 0.8 * final_price_of_house, 500)
        if final_price_of_house <= 30000:
            legal_fees = final_price_of_house * 0.9 / 1000
        elif final_price_of_house <= 60000:
            legal_fees = 30 + (final_price_of_house - 30000) * 0.72 / 1000
        else:
            legal_fees = 72 + (final_price_of_house - 60000) * 0.6 / 1000

        total_key_collection_payment = second_downpayment + renovation_fee + lease_in_escrow + survey_fees + stamp_duty_deed_assignment + legal_fees

        # Housing Loan
        loan_amount = 0.8 * final_price_of_house
        monthly_repayment = npf.pmt(0.026 / 12, 25 * 12, -loan_amount)  # Use numpy_financial.pmt
        home_protection = 18.67
        if room_type == "4 ROOM":
            fire_insurance = 5.99 / 60
        elif room_type == "5 ROOM":
            fire_insurance = 7.19 / 60
        else:
            fire_insurance = 4.91 / 60
        total_monthly_payment = monthly_repayment + home_protection + fire_insurance

        results = {
            "Husband Monthly CPF OA": husband_monthly_cpf_oa,
            "Wife Monthly CPF OA": wife_monthly_cpf_oa,
            "Amount CPF Husband to Key Collection": amount_cpf_husband_to_key_collection,
            "Amount CPF Wife to Key Collection": amount_cpf_wife_to_key_collection,
            "Enhanced CPF Grant": enhanced_cpf_grant,
            "PLH Grant": plh_grant,
            "Final Price of House": final_price_of_house,
            "Option Fee": option_fee,
            "First Downpayment": first_downpayment,
            "Stamp Duty": stamp_duty,
            "Total First Payment": total_first_payment,
            "Second Downpayment": second_downpayment,
            "Renovation Fee": renovation_fee,
            "Lease in Escrow": lease_in_escrow,
            "Survey Fees": survey_fees,
            "Stamp Duty Deed Assignment": stamp_duty_deed_assignment,
            "Legal Fees": legal_fees,
            "Total Key Collection Payment": total_key_collection_payment,
            "Monthly Repayment": monthly_repayment,
            "Home Protection": home_protection,
            "Fire Insurance": fire_insurance,
            "Total Monthly Payment": total_monthly_payment
        }

        return render_template('results.html', results=results)
    else:
        # Prepare data for the form (e.g., months, years, options)
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        current_year = datetime.datetime.now().year
        years = [year for year in range(current_year - 50, current_year + 51)]
        # Set default years
        default_work_year = 2024
        default_bto_completion_year = 2028

        return render_template('index.html', months=months, years=years,
                               current_year=current_year,
                               default_work_year=default_work_year,
                               default_bto_completion_year=default_bto_completion_year)

if __name__ == '__main__':
    app.run(debug=True)
