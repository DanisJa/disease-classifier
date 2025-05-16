# NOT WORKING ENTIRLEY!
import requests

# Search for structured product labels by drug name
def search_spls(drug_name):
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug_name}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Error fetching SPLs:", response.status_code)
        return []

    try:
        data = response.json()
        return data["data"] if "data" in data else []
    except Exception as e:
        print("❌ JSON decode error in SPL search:", e)
        print("Raw response:", response.text)
        return []

# Get full drug label using setid
def get_label(setid):
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.json"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Error fetching label:", response.status_code)
        return None

    try:
        return response.json()
    except Exception as e:
        print("❌ Failed to parse label JSON:", e)
        print("Raw response:", response.text)
        return None

# Extract and print meaningful drug sections
def print_label_sections(label_info):
    try:
        sections = label_info["data"]["sections"]
        for section in sections:
            title = section.get("title", "").strip()
            text = section.get("text", "").strip()
            if title.lower() in ["indications and usage", "dosage and administration", "warnings", "contraindications"]:
                print(f"\n=== {title} ===")
                print(text[:1000] + ("..." if len(text) > 1000 else ""))  # Limit output
    except Exception as e:
        print("⚠️ Error extracting sections:", e)

# Main program
if __name__ == "__main__":
    drug_name = input("Enter drug name (e.g., metformin): ").strip()
    spls = search_spls(drug_name)

    if not spls:
        print("❌ No SPL data found.")
    else:
        first = spls[0]
        print(f"\n✅ Found: {first['title']}")
        print(f"Set ID: {first['setid']}")

        label_info = get_label(first["setid"])

        if label_info:
            print(f"\n📄 Drug Title: {label_info['data']['title']}")
            print_label_sections(label_info)
        else:
            print("❌ Failed to fetch detailed label.")
