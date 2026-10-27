#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

#%%
# Define cities and years
cities = ["adana", "adıyaman", "diyarbakır", "gaziantep", "hatay", "kahramanmaraş", "kilis", "malatya", "osmaniye", "şanlıurfa"]
years = [1983, 1987, 1991, 1995, 1999, 2002, 2007, 2011, 2015, 2018]

# Base URL structure for Wikipedia
base_url = "https://tr.wikipedia.org/wiki/{}%27da_{}_Türkiye_genel_seçimleri"

# Initialize an empty list to store data
all_data = []

# Loop through each city and year
for city in cities:
    for year in years:
        if city == "kahramanmaraş":
            url = f"https://tr.wikipedia.org/wiki/{city.capitalize()}%27ta_{year}_Türkiye_genel_seçimleri"
        elif city == "gaziantep":
            url = f"https://tr.wikipedia.org/wiki/{city.capitalize()}%27te_{year}_Türkiye_genel_seçimleri"
        else:
            url = f"https://tr.wikipedia.org/wiki/{city.capitalize()}%27da_{year}_Türkiye_genel_seçimleri"

        print(f"Scraping: {url}")  # Debugging message

        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if request was successful
            soup = BeautifulSoup(response.content, "html.parser")

            # Find the specific table under the section "İlçelerde en yüksek oyu alanlar"
            header = soup.find("h2", id="İlçelerde_en_yüksek_oyu_alanlar")

            if header:
                table = header.find_next("table", {"class": "wikitable"})
                rows = table.find_all("tr")

                last_party = None  # Variable to store last seen party (for rowspan)

                for row in rows[1:]:  # Skip the header row
                    cols = row.find_all("td")

                    if len(cols) == 1:
                        # If only one column is present (due to rowspan), reuse last party
                        ilce = cols[0].text.strip()
                    elif len(cols) == 2:
                        # Normal case with both columns
                        ilce = cols[0].text.strip()
                        last_party = cols[1].text.strip()  # Update last seen party

                    if last_party:  # Ensure we have a party value
                        all_data.append([city.capitalize(), ilce, f"WP.{year}", last_party])  # Append data

                time.sleep(1)  # Pause to avoid overwhelming Wikipedia's servers

            else:
                print(f"Table not found for {city} in {year}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")

# Create DataFrame
df = pd.DataFrame(all_data, columns=["Province", "İlçe", "Year", "Party"])

# Pivot table to get short format
df_pivot = df.pivot_table(index=["Province", "İlçe"], columns="Year", values="Party", aggfunc="first").reset_index()

# Rename columns for clarity
df_pivot.columns = ["Province", "İlçe"] + [col for col in df_pivot.columns[2:]]

# Fill missing values with "N/A"
df_pivot = df_pivot.fillna("N/A")

# Save to excel
df_pivot.to_excel("/Users/nihankaragul/Documents/Documents - Nihan’s MacBook Air/2024 Fall/Dissertation/Data/Election_results/ilce_election.xlsx", index=False)

print("Scraping complete! Data saved to 'ilce_election.xlsx')

#%%
# Define years and provinces
years = [1984, 1989, 1994, 1999, 2004, 2009, 2014, 2019]
provinces = ["adana", "adıyaman", "diyarbakır", "gaziantep", "hatay", "kahramanmaraş", "kilis", "malatya", "osmaniye",
             "şanlıurfa"]

# List to store all data
all_data = []

# Loop over years and provinces
for year in years:
    for province in provinces:
        # Handle special cases for URL structure
        if province == "gaziantep":
            url = f"https://tr.wikipedia.org/wiki/{province.capitalize()}%27te_{year}_Türkiye_yerel_seçimleri"
        elif province == "osmaniye":
            url = f"https://tr.wikipedia.org/wiki/{province.capitalize()}%27de_{year}_Türkiye_yerel_seçimleri"
        elif province == "kilis":
            url = f"https://tr.wikipedia.org/wiki/{province.capitalize()}%27te_{year}_Türkiye_yerel_seçimleri"
        elif province == "kahramanmaraş":
            url = f"https://tr.wikipedia.org/wiki/{province.capitalize()}%27ta_{year}_Türkiye_yerel_seçimleri"
        else:
            url = f"https://tr.wikipedia.org/wiki/{province.capitalize()}%27da_{year}_Türkiye_yerel_seçimleri"

        print(f"Scraping: {url}")

        # Fetch the page content
        response = requests.get(url)

        # If the page does not exist, mark all districts as "N/A"
        if response.status_code != 200:
            print(f"Skipping {province} in {year} (Page not found)")
            all_data.append({"Province": province.capitalize(), "District": "N/A", f"LE.{year}": "N/A"})
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        # Step 1: Extract all districts (Look for <h3> and <h2> as Wikipedia structures differ)
        districts = []
        tables = []

        for header in soup.find_all(["h3", "h2"]):  # Some years use h2 instead of h3
            district_name = header.text.strip()

            # Find the next table related to this district
            next_table = header.find_next("table", class_="wikitable")

            if next_table:
                districts.append(district_name)
                tables.append(next_table)

        # If no districts are found, mark the province as "N/A" for that year
        if not districts:
            print(f"No district data for {province} in {year}")
            all_data.append({"Province": province.capitalize(), "District": "N/A", f"LE.{year}": "N/A"})
            continue

        # Step 2: Extract winning party from each table
        for district, table in zip(districts, tables):
            rows = table.find_all("tr")[2:]  # Skip the first two header rows

            max_votes = 0
            winning_party = None

            for row in rows:
                cols = row.find_all("td")

                if len(cols) >= 5:  # Ensure row has vote data
                    party_name = cols[2].get_text(strip=True)

                    try:
                        votes = int(cols[4].get_text(strip=True).replace(".", "").replace(",", ""))
                    except ValueError:
                        votes = 0  # Handle cases where vote count is missing

                    if votes > max_votes:
                        max_votes = votes
                        winning_party = party_name

            if winning_party:
                all_data.append({"Province": province.capitalize(), "District": district, f"LE.{year}": winning_party})
            else:
                all_data.append({"Province": province.capitalize(), "District": district, f"LE.{year}": "N/A"})

        # Delay to avoid being blocked by Wikipedia
        time.sleep(1)

# Convert to DataFrame
df = pd.DataFrame(all_data)
print(df)

df.to_excel('/Users/nihankaragul/Documents/Documents - Nihan’s MacBook Air/2024 Fall/Dissertation/Data/Election_results/ilce_LOCALelection.xlsx', index=False)
#%%
df = pd.read_excel('/Users/nihankaragul/Documents/Documents - Nihan’s MacBook Air/2024 Fall/Dissertation/Data/Election_results/ilce_LOCALelection.xlsx')

#%%
# Pivot the data to group by unique Province and District
df_pivot = df.pivot_table(index=["Province", "District"],
                          values=[col for col in df.columns if col.startswith("LE.")],
                          aggfunc="first").reset_index()
df_pivot.to_excel('/Users/nihankaragul/Documents/Documents - Nihan’s MacBook Air/2024 Fall/Dissertation/Data/Election_results/ilce_LOCALelection_pv.xlsx', index=False)
