import pandas as pd
import numpy as np

np.random.seed(42)

venues = {
    "Main Auditorium": {"cap": 800, "block": "Audi Block", "av": ["Full Sound + LED Wall", "Standard AV + Projector"]},
    "KE Auditorium": {"cap": 500, "block": "Block IV", "av": ["Full Sound + LED Wall", "Standard AV + Projector"]},
    "Skyview": {"cap": 250, "block": "Central Block", "av": ["Standard AV + Projector", "Basic Mic + Screen"]},
    "Panel Room 1": {"cap": 100, "block": "Block II", "av": ["Basic Mic + Screen", "Standard AV + Projector"]},
    "Panel Room 2": {"cap": 100, "block": "Block II", "av": ["Basic Mic + Screen"]},
    "Assembly Hall": {"cap": 300, "block": "Block I", "av": ["Standard AV + Projector", "Basic Mic + Screen"]}
}

departments = [
    "Computer Science", "Management", "Commerce", "Psychology", 
    "Law", "Physics", "Life Sciences", "Student Council", "Media Studies"
]

event_types = [
    "National Fest", "Guest Lecture", "Workshop", "Seminar", 
    "Cultural Audition", "Hackathon", "Panel Discussion", "Conclave"
]

num_rows = 150
dates = pd.date_range(start="2026-08-01", end="2026-11-30", freq="D")
chosen_dates = np.sort(np.random.choice(dates, size=num_rows))

records = []
for i in range(num_rows):
    evt_id = f"EVT-{1001 + i}"
    dept = np.random.choice(departments)
    etype = np.random.choice(event_types)
    
    if etype in ["National Fest", "Cultural Audition", "Conclave"]:
        venue = np.random.choice(["Main Auditorium", "KE Auditorium"], p=[0.6, 0.4])
    elif etype in ["Hackathon", "Seminar", "Guest Lecture"]:
        venue = np.random.choice(["KE Auditorium", "Skyview", "Assembly Hall"], p=[0.3, 0.4, 0.3])
    else:
        venue = np.random.choice(["Skyview", "Panel Room 1", "Panel Room 2", "Assembly Hall"], p=[0.2, 0.35, 0.35, 0.1])
        
    cap = venues[venue]["cap"]
    block = venues[venue]["block"]
    av = np.random.choice(venues[venue]["av"])
    
    date_str = pd.Timestamp(chosen_dates[i]).strftime("%Y-%m-%d")
    start_hr = int(np.random.choice([9, 10, 11, 13, 14, 15]))
    duration = int(np.random.choice([2, 3, 4, 6], p=[0.45, 0.3, 0.15, 0.1]))
    end_hr = min(start_hr + duration, 19)
    
    expected_footfall = int(cap * np.random.uniform(0.45, 0.98))
    
    if pd.Timestamp(chosen_dates[i]) < pd.Timestamp("2026-11-18"):
        status = np.random.choice(["Completed", "Cancelled", "Clash Flagged"], p=[0.85, 0.08, 0.07])
    else:
        status = np.random.choice(["Scheduled", "Clash Flagged"], p=[0.88, 0.12])
        
    actual_footfall = min(int(expected_footfall * np.random.uniform(0.8, 1.05)), cap) if status == "Completed" else 0
    power_kwh = round((end_hr - start_hr) * (cap * 0.015) * np.random.uniform(0.9, 1.1), 1)
    evt_name = f"{dept.split()[0]} {etype} #{np.random.randint(1, 15)}"
    
    records.append({
        "Event_ID": evt_id,
        "Event_Name": evt_name,
        "Department": dept,
        "Event_Type": etype,
        "Venue": venue,
        "Block": block,
        "Venue_Capacity": cap,
        "Date": date_str,
        "Start_Hour": start_hr,
        "End_Hour": end_hr,
        "Expected_Footfall": expected_footfall,
        "Actual_Footfall": actual_footfall,
        "AV_Setup": av,
        "Est_Power_kWh": power_kwh,
        "Booking_Status": status
    })

df = pd.DataFrame(records)
df.to_csv("christ_campus_events.csv", index=False)
print("Dataset saved successfully:", df.shape)