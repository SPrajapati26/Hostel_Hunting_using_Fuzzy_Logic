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
│
├── READ_ME.md
```
## Project Files

- app.py –>  web application
- fuzzy_engine.py –> Fuzzy recommendation engine
- data/bern_hostel_complete_dataset.csv –> Hostel dataset
- templates/index.html –> Frontend HTML files
- requirements.txt -> required packages to run the project


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

- Traveler Type (Backpacker, Social Butterfly, Digital Nomad)
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

  

