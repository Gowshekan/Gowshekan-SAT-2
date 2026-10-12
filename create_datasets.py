from pathlib import Path
import pandas as pd
import numpy as np
import random
import calendar

# These are SYNTHETIC practice records, not real hospital patient data.
random.seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dataset"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# 1. Patients
# -------------------------
n_patients = 250
patient_ids = [f"P{i:04d}" for i in range(1, n_patients + 1)]
age_groups = ["Under 18", "18-29", "30-44", "45-59", "60+"]
localities = ["Urban", "Semi-Urban", "Rural"]

patients = pd.DataFrame({
    "patient_id": patient_ids,
    "age_group": np.random.choice(age_groups, n_patients, p=[0.08, 0.22, 0.28, 0.24, 0.18]),
    "locality": np.random.choice(localities, n_patients, p=[0.50, 0.30, 0.20]),
    "visit_history": np.random.choice(["New Patient", "Returning Patient"], n_patients, p=[0.35, 0.65])
})
patients.to_csv(DATA_DIR / "patients.csv", index=False)

# -------------------------
# 2. Doctors
# -------------------------
specialties = ["Cardiology", "Neurology", "Orthopedics", "Dermatology", "Pediatrics"]
doctors_rows = []
for i in range(1, 16):
    specialty = specialties[(i - 1) % len(specialties)]
    doctors_rows.append({
        "doctor_id": f"D{i:03d}",
        "doctor_name": f"Doctor {i:02d}",
        "specialty": specialty,
        "clinic_schedule": random.choice(["Morning", "Afternoon", "Full Day"]),
        "available_hours_per_week": random.choice([12, 16, 20, 24, 30])
    })
doctors = pd.DataFrame(doctors_rows)
doctors.to_csv(DATA_DIR / "doctors.csv", index=False)

# -------------------------
# 3. Calendar
# -------------------------
dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
holiday_dates = set(pd.to_datetime([
    "2025-01-01", "2025-01-14", "2025-01-26", "2025-04-14",
    "2025-05-01", "2025-08-15", "2025-10-02", "2025-12-25"
]).date)
calendar_df = pd.DataFrame({"date": dates})
calendar_df["weekday"] = calendar_df["date"].dt.day_name()
calendar_df["is_holiday"] = calendar_df["date"].dt.date.isin(holiday_dates)
calendar_df["season"] = calendar_df["date"].dt.month.map({
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon"
})
calendar_df.to_csv(DATA_DIR / "calendar.csv", index=False)

# -------------------------
# 4. Appointments
# -------------------------
n_appointments = 1200
departments = ["Cardiology", "Neurology", "Orthopedics", "Dermatology", "Pediatrics"]
appointment_rows = []
start = pd.Timestamp("2025-01-01")
end = pd.Timestamp("2025-12-31")
date_range_days = (end - start).days

for i in range(1, n_appointments + 1):
    patient_id = random.choice(patient_ids)
    doctor = random.choice(doctors_rows)
    department = doctor["specialty"]
    appointment_date = start + pd.Timedelta(days=random.randint(0, date_range_days))
    waiting_days = random.choices([0, 1, 3, 7, 14, 21, 30, 45], weights=[8, 12, 16, 20, 16, 10, 10, 8])[0]
    booking_date = appointment_date - pd.Timedelta(days=waiting_days)
    # Illustrative probability pattern: longer waits slightly increase no-show likelihood.
    no_show_probability = 0.12 + min(waiting_days, 45) * 0.003
    status = random.choices(["Attended", "No-show", "Cancelled"], weights=[
        max(0.1, 0.78 - no_show_probability), no_show_probability, 0.22
    ])[0]
    appointment_rows.append({
        "appointment_id": f"A{i:05d}",
        "patient_id": patient_id,
        "doctor_id": doctor["doctor_id"],
        "appointment_date": appointment_date.strftime("%Y-%m-%d"),
        "booking_date": booking_date.strftime("%Y-%m-%d"),
        "department": department,
        "status": status
    })

appointments = pd.DataFrame(appointment_rows)

# Add data-quality issues deliberately for cleaning practice.
# 1) Missing appointment status
appointments.loc[4, "status"] = np.nan
appointments.loc[58, "status"] = np.nan

# 2) Inconsistent department spelling/capitalization
appointments.loc[15, "department"] = " cardiology "
appointments.loc[80, "department"] = "NEUROLOGY"
appointments.loc[155, "department"] = "Orthopaedics"

# 3) Invalid waiting time by setting a booking date after the appointment date
appointments.loc[22, "booking_date"] = (
    pd.to_datetime(appointments.loc[22, "appointment_date"]) + pd.Timedelta(days=5)
).strftime("%Y-%m-%d")

# 4) Duplicate booking row (deliberate exact duplicate)
appointments = pd.concat([appointments, appointments.iloc[[10]]], ignore_index=True)

appointments.to_csv(DATA_DIR / "appointments.csv", index=False)

# -------------------------
# 5. Reminders
# -------------------------
reminder_rows = []
reminder_types = ["SMS", "Phone Call", "Email"]
for _, row in appointments.iterrows():
    # Not every appointment has a reminder record.
    if random.random() < 0.78:
        sent_status = random.choice(["Sent", "Failed", "Not Sent"])
        response = random.choice(["Confirmed", "No Response", "Requested Reschedule", ""])
        reminder_rows.append({
            "reminder_id": f"R{len(reminder_rows) + 1:05d}",
            "appointment_id": row["appointment_id"],
            "reminder_type": random.choice(reminder_types),
            "sent_status": sent_status,
            "response": response
        })

reminders = pd.DataFrame(reminder_rows)
# Add an incomplete reminder record for data-quality practice.
if len(reminders) > 0:
    reminders.loc[3, "sent_status"] = np.nan
    reminders.loc[8, "response"] = np.nan
reminders.to_csv(DATA_DIR / "reminders.csv", index=False)

print("Synthetic practice datasets created successfully!")
print(f"Folder: {DATA_DIR}")
for file_name in ["appointments.csv", "patients.csv", "doctors.csv", "reminders.csv", "calendar.csv"]:
    df = pd.read_csv(DATA_DIR / file_name)
    print(f"{file_name}: {len(df)} rows, {len(df.columns)} columns")
print("\nReminder: these records are synthetic practice data, not real hospital records.")
