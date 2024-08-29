import sqlite3
from tabulate import tabulate
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import folium
from textblob import TextBlob


DATABASE = 'DIA.db'


def connect_db():
  try:
    connection = sqlite3.connect(DATABASE)
    return connection
  except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
    return None


def fetch_data(query):
  connection = connect_db()
  if connection:
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data
  else:
    return []


def display_results():
  print("Fetching results from the most recent analysis...\n")

  # Fetching data from Image_Txt_Results table
  image_results = fetch_data("SELECT * FROM Image_Txt_Results ORDER BY create_date DESC LIMIT 50")
  print("Image_Txt_Results Table:")
  print(tabulate(image_results,
                 headers=["ID", "Transaction ID", "Result Type", "Male Count", "Female Count", "Confidence",
                          "Skin Color", "Race", "Image Link", "Create Date"], tablefmt="pretty"))
  print("\n")

  # Fetching data from biased_text_results table, including the source column
  text_results = fetch_data(
    "SELECT id, transaction_id, source, result_type, sentence, word, image_link, create_date FROM biased_text_results WHERE result_type != 'Geography' ORDER BY create_date DESC LIMIT 50")
  print("biased_text_results Table (Excluding Geography):")
  print(tabulate(text_results,
                 headers=["ID", "Transaction ID", "Source", "Result Type", "Sentence", "Word", "Image Link",
                          "Create Date"],
                 tablefmt="pretty"))
  print("\n")

  # Fetching data from biased_alt_Text_results table
  alt_text_results = fetch_data("SELECT * FROM biased_alt_Text_results ORDER BY create_date DESC LIMIT 50")
  print("biased_alt_Text_results Table:")
  print(tabulate(alt_text_results,
                 headers=["ID", "Transaction ID", "Source", "Result Type", "Sentence", "Word", "Image Link", "Create Date"],
                 tablefmt="pretty"))
  print("\n")

  # Fetching data from biased_img_results table
  img_text_results = fetch_data("SELECT * FROM biased_img_results ORDER BY create_date DESC LIMIT 50")
  print("biased_img_results Table:")
  print(tabulate(img_text_results,
                 headers=["ID", "Transaction ID", "Source", "Result Type", "Sentence", "Word", "Image Link", "Create Date"],
                 tablefmt="pretty"))
  print("\n")

  # Fetching data from geographical_bias table
  geography_results = fetch_data("SELECT * FROM geographical_bias ORDER BY create_date DESC LIMIT 50")
  print("Geographical Bias Results:")
  print(tabulate(geography_results,
                 headers=["ID", "Transaction ID", "Source", "Geo Entity", "Entity Type", "Create Date"],
                 tablefmt="pretty"))
  print("\n")


def generate_report():
  # Fetch and display Image_Txt_Results
  image_results = fetch_data("SELECT * FROM Image_Txt_Results ORDER BY create_date DESC LIMIT 50")
  print("Image_Txt_Results Table:")
  print(tabulate(image_results,
                 headers=["ID", "Transaction ID", "Result Type", "Male Count", "Female Count", "Confidence",
                          "Skin Color", "Race", "Image Link", "Create Date"], tablefmt="pretty"))
  print("\n")

  # Fetch and display biased_text_results (excluding Geography)
  text_results = fetch_data(
    "SELECT * FROM biased_text_results WHERE result_type != 'Geography' ORDER BY create_date DESC LIMIT 50")
  print("biased_text_results Table (Excluding Geography):")
  print(tabulate(text_results,
                 headers=["ID", "Transaction ID", "Source", "Result Type", "Sentence", "Word", "Image Link",
                          "Create Date"],
                 tablefmt="pretty"))
  print("\n")

  # Fetch and display biased_alt_Text_results
  alt_text_results = fetch_data("SELECT * FROM biased_alt_Text_results ORDER BY create_date DESC LIMIT 50")
  print("biased_alt_Text_results Table:")
  print(tabulate(alt_text_results,
                 headers=["ID", "Transaction ID", "Source", "Result Type", "Sentence", "Word", "Image Link",
                          "Create Date"],
                 tablefmt="pretty"))
  print("\n")

  # Fetch and display biased_img_results
  img_text_results = fetch_data("SELECT * FROM biased_img_results ORDER BY create_date DESC LIMIT 50")
  print("biased_img_results Table:")
  print(tabulate(img_text_results,
                 headers=["ID", "Transaction ID", "Source", "Result Type", "Sentence", "Word", "Image Link",
                          "Create Date"],
                 tablefmt="pretty"))
  print("\n")

  # Fetch and display Geographical Bias Results
  geography_results = fetch_data("SELECT * FROM geographical_bias ORDER BY create_date DESC LIMIT 50")
  print("Geographical Bias Results:")
  print(
    tabulate(geography_results, headers=["ID", "Transaction ID", "Source", "Geo Entity", "Entity Type", "Create Date"],
             tablefmt="pretty"))
  print("\n")

  # Additional Analysis: Gender Distribution
  gender_distribution()

  # Additional Analysis: Confidence Level Analysis
  confidence_level_analysis()

  # Additional Analysis: Word Frequency Analysis
  word_frequency_analysis()

  # Additional Analysis: Skin Color and Race Distribution
  skin_race_distribution()

  # Additional Analysis: Geographical Bias Frequency
  geographical_bias_frequency()

  # Additional Analysis: Temporal Analysis
  temporal_analysis()

  # Additional Analysis: Source-Based Analysis
  source_based_analysis()

  # Additional Analysis: Co-occurrence Analysis
  co_occurrence_analysis()

  # Additional Analysis: Bias Severity Analysis
  bias_severity_analysis()

  # Additional Analysis: Sentiment Analysis
  sentiment_analysis()

  # Additional Analysis: Geographical Bias Heatmap
  geographical_heatmap()


def temporal_analysis():
  query = """
        SELECT DATE(create_date), COUNT(*)
        FROM biased_text_results
        GROUP BY DATE(create_date)
        ORDER BY DATE(create_date) DESC
    """
  data = fetch_data(query)
  dates, counts = zip(*data)

  plt.figure(figsize=(10, 6))
  plt.plot(dates, counts, marker='o')
  plt.title('Temporal Analysis of Biased Text Results')
  plt.xlabel('Date')
  plt.ylabel('Frequency')
  plt.xticks(rotation=45)
  plt.tight_layout()
  plt.show()


def sentiment_analysis():
  # Fetch text data from the biased_text_results table
  text_data = fetch_data("SELECT sentence FROM biased_text_results WHERE result_type != 'Geography'")

  if not text_data:
    print("No text data available for sentiment analysis.")
    return

  # Analyze sentiment for each sentence
  sentiments = []
  for row in text_data:
    sentence = row[0]
    blob = TextBlob(sentence)
    sentiment_score = blob.sentiment.polarity
    sentiments.append(sentiment_score)

  # Generate a histogram to show sentiment distribution
  plt.figure(figsize=(8, 6))
  plt.hist(sentiments, bins=10, color='purple', alpha=0.7)
  plt.title('Sentiment Analysis of Text Data')
  plt.xlabel('Sentiment Score')
  plt.ylabel('Frequency')
  plt.show()

  # Print out the average sentiment score
  average_sentiment = np.mean(sentiments)
  print(f"Average Sentiment Score: {average_sentiment:.2f}")


def source_based_analysis():
  query = """
        SELECT source, COUNT(*)
        FROM biased_text_results
        GROUP BY source
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """
  data = fetch_data(query)
  sources, counts = zip(*data)

  plt.figure(figsize=(10, 6))
  plt.bar(sources, counts, color='purple')
  plt.title('Top 10 Sources Contributing to Bias')
  plt.xlabel('Source')
  plt.ylabel('Frequency')
  plt.xticks(rotation=45)
  plt.tight_layout()
  plt.show()


def co_occurrence_analysis():
  query = """
        SELECT word, COUNT(*)
        FROM (
            SELECT word FROM biased_text_results
            UNION ALL
            SELECT word FROM biased_alt_Text_results
            UNION ALL
            SELECT word FROM biased_img_results
        )
        GROUP BY word
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """
  data = fetch_data(query)
  words, counts = zip(*data)

  plt.figure(figsize=(10, 6))
  plt.bar(words, counts, color='red')
  plt.title('Top 10 Co-occurring Words in Biased Text')
  plt.xlabel('Word')
  plt.ylabel('Co-occurrence Count')
  plt.xticks(rotation=45)
  plt.tight_layout()
  plt.show()


def bias_severity_analysis():
  # Verify that the column exists and the correct table is being queried
  query = """
  SELECT result_type, AVG(confidence) as avg_confidence
  FROM Image_Txt_Results
  GROUP BY result_type
  """

  # If the column doesn't exist, this query will need to be adjusted
  data = fetch_data(query)

  if not data:
    print("No data available for bias severity analysis.")
    return

  result_types = [row[0] for row in data]
  avg_confidences = [row[1] for row in data]

  plt.figure(figsize=(10, 6))
  plt.bar(result_types, avg_confidences, color='red')
  plt.title('Bias Severity Analysis')
  plt.xlabel('Result Type')
  plt.ylabel('Average Confidence')
  plt.show()


def geographical_heatmap():
  geo_data = fetch_data("SELECT geo_entity FROM geographical_bias")
  geo_entities = [row[0] for row in geo_data]
  geo_counts = Counter(geo_entities)

  # Create a basic world map
  m = folium.Map(location=[0, 0], zoom_start=2)

  # Add points to the map
  for entity, count in geo_counts.items():
    # Example: Adding random latitude and longitude; replace with actual coordinates for each geo entity
    folium.CircleMarker(location=[np.random.uniform(-90, 90), np.random.uniform(-180, 180)],
                        radius=count,
                        color='red',
                        fill=True,
                        fill_opacity=0.6,
                        popup=f'{entity}: {count} biases').add_to(m)

  m.save('geographical_bias_heatmap.html')


def gender_distribution():
  # Example sizes list with NaN check
  sizes = [5, 10, np.nan, 0]  # Replace with actual sizes data
  labels = ['Male', 'Female', 'Unknown', 'Other']  # Replace with actual labels

  # Remove NaN and zero values from sizes and their corresponding labels
  valid_indices = [i for i, size in enumerate(sizes) if not np.isnan(size) and size > 0]
  sizes = [sizes[i] for i in valid_indices]
  labels = [labels[i] for i in valid_indices]

  if len(sizes) == 0:
    print("No valid data available for plotting.")
    return

  plt.figure(figsize=(6, 6))
  plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
  plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
  plt.title('Gender Distribution')
  plt.show()


def confidence_level_analysis():
  confidence_data = fetch_data("SELECT confidence FROM Image_Txt_Results")
  confidences = [row[0] for row in confidence_data]

  plt.figure(figsize=(8, 6))
  plt.hist(confidences, bins=10, color='blue', alpha=0.7)
  plt.title('Confidence Level Distribution')
  plt.xlabel('Confidence')
  plt.ylabel('Frequency')
  plt.show()


def word_frequency_analysis():
  word_data = fetch_data(
    "SELECT word FROM biased_text_results UNION ALL SELECT word FROM biased_alt_Text_results UNION ALL SELECT word FROM biased_img_results")
  words = [row[0] for row in word_data]
  word_counts = Counter(words)
  top_words = word_counts.most_common(10)

  if not top_words:
    print("No words found for analysis.")
    return [], []

  words, counts = zip(*top_words)
  plt.bar(words, counts)
  plt.xlabel("Words")
  plt.ylabel("Frequency")
  plt.title("Top 10 Words Frequency")
  plt.show()
  return words, counts


def skin_race_distribution():
  skin_color_data = fetch_data("SELECT skin_color FROM Image_Txt_Results")
  race_data = fetch_data("SELECT race FROM Image_Txt_Results")

  skin_colors = [row[0] for row in skin_color_data]
  races = [row[0] for row in race_data]

  skin_color_counts = Counter(skin_colors)
  race_counts = Counter(races)

  plt.figure(figsize=(10, 6))

  plt.subplot(1, 2, 1)
  plt.bar(skin_color_counts.keys(), skin_color_counts.values(), color='brown')
  plt.title('Skin Color Distribution')
  plt.xlabel('Skin Colors')
  plt.ylabel('Frequency')

  plt.subplot(1, 2, 2)
  plt.bar(race_counts.keys(), race_counts.values(), color='green')
  plt.title('Race Distribution')
  plt.xlabel('Races')
  plt.ylabel('Frequency')

  plt.tight_layout()
  plt.show()


def geographical_bias_frequency():
  geo_data = fetch_data("SELECT geo_entity FROM geographical_bias")
  geo_entities = [row[0] for row in geo_data]
  geo_counts = Counter(geo_entities)

  top_geo_entities = geo_counts.most_common(10)

  entities, counts = zip(*top_geo_entities)

  plt.figure(figsize=(10, 6))
  plt.bar(entities, counts, color='orange')
  plt.title('Top 10 Geographical Entities Frequency')
  plt.xlabel('Geographical Entities')
  plt.ylabel('Frequency')
  plt.show()


def main():
  display_results()


if __name__ == "__main__":
  main()
  generate_report()
