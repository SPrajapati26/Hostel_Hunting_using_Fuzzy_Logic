#  Hostel Hunting using Fuzzy Logic

The  Hostel Hunter is a web-based application that uses Fuzzy Logic to provide personalized hostel recommendations.
Unlike traditional filtering systems, the application evaluates multiple criteria simultaneously and recommends hostels based on how closely they match the user's preferences.

## Technologies Used

- Python
- Flask
- Pandas
- NumPy
- HTML/CSS/JavaScript
- Custom Fuzzy Logic Engine

## Project Structure

```
Hostel_Hunting_using_Fuzzy/
│
├── app.py
├── fuzzy_engine.py
├── requirements.txt
│
├── templates/
│   └── index.html
│
├── data/
│   └── bern_hostel_complete_dataset.csv
│   └── zurich_hostel_complete_dataset.csv
│
├── Reports/
│   └── Pre-Implementation Evaluation.pdf
│   └── Post-Implementation Evaluation.pdf
│   └── Hostel_Hunting_UI_Flow.pdf
│   └── hostel_hunting_internal_working.pdf
│
│  
├── READ_ME.md
│
```
## Project Files

- app.py –>  web application
- fuzzy_engine.py –> Fuzzy recommendation engine
- data/bern_hostel_complete_dataset.csv –> Hostel dataset for city Bern
- data/bern_hostel_complete_dataset.csv –> Hostel dataset for city Zurich
- templates/index.html –> Frontend HTML files
- requirements.txt -> required packages to run the project
- Reports -> Pre-Implementation Evaluation.pdf ( fuzzy logic is working fine or not for the project)
- Reports -> Post-Implementation Evaluation.pdf ( Includes implemenation results and user survey & feedback and how is helpful for them)
- Reports -> Hostel_Hunting_UI_Flow.pdf ( How the project flow is working )
- Reports -> hostel_hunting_internal_working.pdf (Internal Working of fuzzy_engine.py)


## Installation

Install the required packages:

--bash--
pip install -r requirements.txt

## Running the Application

Start the application:

--bash--
python app.py


Open your browser and visit:
----------------------
http://localhost:5000
----------------------

## User Inputs

- Traveler Type (Backpacker, Social Butterfly, Worry-Free)
- Budget
- Maximum Distance
- Safety Requirement
- Cleanliness Requirement
- Social Importance
- Wi-Fi Importance
- Breakfast Preference
- Station Preference

## Output

After processing user preferences, the system provides:
- Ranked Hostel List
Hostels sorted according to recommendation score.
- Recommendation Score
A score indicating how well a hostel matches the user's requirements.

- Hostel Details
Information including:
- Price, Distance from city center, Safety rating, Cleanliness rating 
Wi-Fi quality, Social atmosphere, Breakfast availability, nearest Station accessibility
- why this hostel is best

  
