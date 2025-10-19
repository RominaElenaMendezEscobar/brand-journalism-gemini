import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class DataVisualizer:
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset
        self.palette = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
                         "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]
        self.title_news_by_source = "News about iPhone by Source"
        self.x_label_news_by_source = "Number of Articles"
        self.y_label_news_by_source = "Source"
        self.title_news_over_time = "Visualization: News about iPhone over Time"
        self.x_label_news_over_time = "Date"
        self.y_label_news_over_time = "Number of Articles"
        self.title_sentiment_category = "Visualization: Analysis of Sentiment and Category"
        self.x_label_sentiment_category = "Sentiment"
        self.y_label_sentiment_category = "Category"
        self.output_path_news_by_source = "img/news_about_iphone_by_source.png"
        self.output_path_news_over_time = "img/news_over_time.png"
        self.output_path_sentiment_category = "img/sentiment_category_heatmap.png"

    def dataset_plot_news_by_source(self):
        tmp =(
               self.dataset
               .groupby(['source_name'], as_index=False)['title']
               .count()
               .rename(columns={'title':'count'})
               .sort_values(by='count', ascending=False)
       )
        return tmp

    def dataset_plot_news_over_time(self):
       tmp =(
           self.dataset
           .groupby(['date'], as_index=False)['title']
           .count()
           .rename(columns={'title':'count'})
           .sort_values(by='date', ascending=True)
       )
       tmp['date'] = pd.to_datetime(tmp['date'])
       return tmp

    def dataset_plot_sentiment_category(self):
       tmp =(
           self.dataset
           .groupby(['category', 'sentiment'], as_index=False)['title']
           .count()
           .rename(columns={'title':'count'})
       )
       return tmp

    def plot_news_by_source(self):
        plt.figure(figsize=(10, 6))
        dataset = self.dataset_plot_news_by_source()
        sns.barplot(x=dataset['count'], y=dataset['source_name'], palette=self.palette)
        plt.title(self.title_news_by_source)
        plt.xlabel(self.x_label_news_by_source)
        plt.ylabel(self.y_label_news_by_source)
        plt.tight_layout()
        plt.savefig(self.output_path_news_by_source)
        plt.close()
        print(f"✅ Plot saved: {self.output_path_news_by_source}")

    def plot_news_over_time(self):
        plt.figure(figsize=(10, 6))
        dataset = self.dataset_plot_news_over_time()
        sns.lineplot(x=dataset['date'], y=dataset['count'], marker='o', color=self.palette[0])
        plt.title(self.title_news_over_time)
        plt.xlabel(self.x_label_news_over_time)
        plt.ylabel(self.y_label_news_over_time)
        plt.tight_layout()
        plt.savefig(self.output_path_news_over_time)
        plt.close()
        print(f"✅ Plot saved: {self.output_path_news_over_time}")

    def plot_sentiment_category_heatmap(self):
        dataset = self.dataset_plot_sentiment_category()
        plt.figure(figsize=(10, 6))
        pivot_table = pd.crosstab(dataset['category'], dataset['sentiment'])
        sns.heatmap(pivot_table, annot=True, fmt="d", cmap="Purples")
        plt.title(self.title_sentiment_category)
        plt.xlabel(self.x_label_sentiment_category)
        plt.ylabel(self.y_label_sentiment_category)
        plt.tight_layout()
        plt.savefig(self.output_path_sentiment_category)
        plt.close()
        print(f"✅ Plot saved: {self.output_path_sentiment_category}")