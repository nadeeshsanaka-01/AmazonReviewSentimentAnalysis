import streamlit as st
import pandas as pd
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import matplotlib.pyplot as plt
import altair as alt


nltk.download('vader_lexicon')


vader = SentimentIntensityAnalyzer()


category_map = {
   'acs': 'Air Conditioners',
   'air-purifiers': 'Air Purifiers',
   'beds': 'Beds',
   'blankets': 'Blankets',
   'blenders': 'Blenders',
   'cameras': 'Cameras',
   'chairs': 'Chairs',
   'chimneys': 'Kitchen Chimneys',
   'clocks': 'Clocks',
   'cookers': 'Pressure Cookers',
   'coolers': 'Air Coolers',
   'dishwashers': 'Dishwashers',
   'dolls': 'Dolls',
   'earphones': 'Earphones',
   'fans': 'Fans',
   'food-processors': 'Food Processors',
   'geysers': 'Water Heaters (Geysers)',
   'induction-stoves': 'Induction Stoves',
   'inverters': 'Inverters',
   'kettles': 'Electric Kettles',
   'keyboards': 'Keyboards',
   'laptops': 'Laptops',
   'lights': 'Lights',
   'mattresses': 'Mattresses',
   'memory-cards': 'Memory Cards',
   'microwaves': 'Microwave Ovens',
   'mixer': 'Mixer Grinders',
   'mobile-cables': 'Mobile Cables',
   'mobile-covers': 'Mobile Covers',
   'mobile-holders': 'Mobile Holders',
   'monitors': 'Monitors',
   'phone': 'Mobile Phones',
   'power-banks': 'Power Banks',
   'refridgerators': 'Refrigerators',
   'rice-cookers': 'Rice Cookers',
   'sewing-machines': 'Sewing Machines',
   'sofas': 'Sofas',
   'speakers': 'Speakers',
   'tables': 'Tables',
   'toasters': 'Toasters',
   'toys': 'Toys',
   'tv': 'Televisions',
   'vacuum-cleaners': 'Vacuum Cleaners',
   'washingmachines': 'Washing Machines',
   'water-purifiers': 'Water Purifiers',
   'wet-grinder': 'Wet Grinders',
}




def remove_emojis(text):
   if pd.isna(text):
       return text
   emoji_pattern = re.compile(
       "["
       "\U0001F600-\U0001F64F"
       "\U0001F300-\U0001F5FF"
       "\U0001F680-\U0001F6FF"
       "\U0001F1E0-\U0001F1FF"
       "\U00002500-\U00002BEF"
       "\U00002702-\U000027B0"
       "\U000024C2-\U0001F251"
       "]+", flags=re.UNICODE
   )
   return emoji_pattern.sub(r'', text)


def analyze_split_reviews(review):
   if pd.isna(review):
       return []


   parts = [part.strip() for part in review.split('|') if part.strip()]
   results = []


   for part in parts:
       score = vader.polarity_scores(part)
       sentiment = (
           "positive" if score['compound'] > 0.05 else
           "negative" if score['compound'] < -0.05 else
           "neutral"
       )
       results.append({
           'review': part,
           'sentiment': sentiment,
           'score': round(score['compound'], 3)
       })


   return results




@st.cache_data
def load_data():
   df = pd.read_excel('flipkartreviews1.xlsx', engine='openpyxl')
   df = df.drop_duplicates(subset='name', keep='first')
   df = df[df['review'] != "No reviews found"]
   df['review'] = df['review'].str.replace('READ MORE', '', regex=False)
   df['review'] = df['review'].apply(remove_emojis)
   df['category_clean'] = df['category'].map(category_map)
   return df




def main():
   st.set_page_config(page_title="Review Sentiment Analyzer", layout="wide")
   st.title("Review Sentiment Analyzer")


   menu = st.sidebar.radio("Navigation", ["Home", "Analyze Reviews", "Category Analysis", "Compare Products"])
   df = load_data()


   if menu == "Home":
       st.markdown("### 👋 Welcome to the Review Sentiment Analyzer")
       st.write("Use the sidebar to go to the **Analysis** section and explore product reviews!")


   elif menu == "Analyze Reviews":
       st.header("🔍 Analyze Product Reviews")


       categories = sorted(df['category_clean'].dropna().unique())
       selected_category = st.selectbox("Choose a category", categories)


       filtered_df = df[df['category_clean'] == selected_category]
       product_names = sorted(filtered_df['name'].unique())


       selected_product = st.selectbox("Choose a product", product_names)


       if st.button("Review"):
           review_text = filtered_df[filtered_df['name'] == selected_product].iloc[0]['review']
           analysis = analyze_split_reviews(review_text)


           if analysis:
               result_df = pd.DataFrame(analysis)
               st.success(f"Showing {len(result_df)} reviews for **{selected_product}**")
               st.dataframe(result_df, use_container_width=True)
               csv = result_df.to_csv(index=False).encode('utf-8')
               st.download_button(
                   label="📥 Export Reviews as CSV",
                   data=csv,
                   file_name=f"{selected_product}_review_analysis.csv",
                   mime='text/csv'
               )
           else:
               st.warning("No valid reviews to analyze.")


       elif st.button("Show Results"):
           review_text = filtered_df[filtered_df['name'] == selected_product].iloc[0]['review']
           analysis = analyze_split_reviews(review_text)


           if analysis:
               result_df = pd.DataFrame(analysis)
               sentiment_counts = result_df['sentiment'].value_counts().reindex(['positive', 'neutral', 'negative'], fill_value=0)


               # Create figure with fixed size
               plt.figure(figsize=(5, 4))
               bars = plt.bar(sentiment_counts.index, sentiment_counts.values, color=['green', 'gray', 'red'])
               plt.title(f"Sentiment Distribution for {selected_product}")
               plt.ylabel("Number of Reviews")
               plt.xlabel("Sentiment")
               plt.tight_layout()


               st.pyplot(plt.gcf())  # Use plt.gcf() to get the current figure


           else:
               st.warning("No valid reviews to visualize.")


   elif menu == "Category Analysis":
       st.header("📊 Category-Level Sentiment Overview")


       categories = sorted(df['category_clean'].dropna().unique())
       selected_category = st.selectbox("Choose a category to analyze", categories)


       filtered_df = df[df['category_clean'] == selected_category]
       products = filtered_df['name'].unique()


       result_list = []


       for product in products:
           product_row = filtered_df[filtered_df['name'] == product].iloc[0]
           review_text = product_row['review']
           link = product_row['link']
           split_reviews = analyze_split_reviews(review_text)
           if split_reviews:
               total_reviews = len(split_reviews)
               positive_reviews = sum(1 for r in split_reviews if r['sentiment'] == 'positive')
               positive_percent = round((positive_reviews / total_reviews) * 100, 2)


               result_list.append({
                   'Product Name': product,
                   'Positive Reviews (%)': positive_percent,
                   'Total Reviews': total_reviews,
                   'Flipkart Link': link
               })


       if result_list:
           result_df = pd.DataFrame(result_list).sort_values(by='Positive Reviews (%)', ascending=False)
           st.markdown("### Product Sentiment Summary")


           for i, row in result_df.iterrows():
               col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
               with col1:
                   st.write(f"**{row['Product Name']}**")
               with col2:
                   st.write(f"{row['Positive Reviews (%)']}%")
               with col3:
                   st.write(f"{row['Total Reviews']} reviews")
               with col4:
                   st.link_button("Flipkart 🔗", row["Flipkart Link"])




   elif menu == "Compare Products":
       st.title("📊 Compare Two Products")
       selected_category = st.selectbox("Select Category", sorted(df['category'].unique()))
       category_products = df[df['category'] == selected_category]['name'].unique()
       col1, col2 = st.columns(2)
       with col1:
           product1 = st.selectbox("Select First Product", category_products, key="product1")
       with col2:
           product2 = st.selectbox("Select Second Product", [p for p in category_products if p != product1], key="product2")


       if st.button("Compare"):
           def get_sentiment_stats(product_name):
               row = df[(df['name'] == product_name) & (df['category'] == selected_category)].iloc[0]
               reviews = analyze_split_reviews(row['review'])
               total = len(reviews)
               positive = sum(1 for r in reviews if r['sentiment'] == 'positive')
               negative = sum(1 for r in reviews if r['sentiment'] == 'negative')
               pos_percent = round((positive / total) * 100, 2) if total else 0
               neg_percent = round((negative / total) * 100, 2) if total else 0
               return {
                   "Product": product_name,
                   "Positive %": pos_percent,
                   "Negative %": neg_percent,
                   "Total Reviews": total,
                   "Link": row['link']
               }


           stats1 = get_sentiment_stats(product1)
           stats2 = get_sentiment_stats(product2)
           sorted_stats = sorted([stats1, stats2], key=lambda x: x["Positive %"], reverse=True)
           st.markdown("### 📦 Product Summary")
           col1, col2 = st.columns(2)
           for stats, col in zip(sorted_stats, [col1, col2]):
               with col:
                   st.markdown(f"#### {stats['Product']}")
                   st.write(f"**Positive Reviews:** {stats['Positive %']}%")
                   st.write(f"**Negative Reviews:** {stats['Negative %']}%")
                   st.write(f"**Total Reviews:** {stats['Total Reviews']}")
                   st.link_button("Flipkart 🔗", stats['Link'])


           st.markdown("### 📈 Sentiment Comparison Charts")
           chart_df = pd.DataFrame({
               "Product": [s["Product"] for s in sorted_stats],
               "Positive %": [s["Positive %"] for s in sorted_stats],
               "Negative %": [s["Negative %"] for s in sorted_stats],
           })
           st.markdown("#### ✅ Positive Reviews")
           positive_chart = (
               alt.Chart(chart_df)
               .mark_bar(size=50, color="green")
               .encode(
                   x=alt.X("Product:N", title=None),
                   y=alt.Y("Positive %:Q", title="Percentage"),
                   tooltip=["Product", "Positive %"]
               )
               .properties(height=300)
           )
           st.altair_chart(positive_chart, use_container_width=True)
           st.markdown("#### ❌ Negative Reviews")
           negative_chart = (
               alt.Chart(chart_df)
               .mark_bar(size=50, color="red")
               .encode(
                   x=alt.X("Product:N", title=None),
                   y=alt.Y("Negative %:Q", title="Percentage"),
                   tooltip=["Product", "Negative %"]
               )
               .properties(height=300)
           )
           st.altair_chart(negative_chart, use_container_width=True)


if __name__ == "__main__":
   main()
