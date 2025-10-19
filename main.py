from brand_journalist_analyzer import BrandJournalistAnalyzer
from report_analysis import ReportAnalysis
from report_plots import DataVisualizer
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv() 
    API_KEY = os.getenv("API_KEY")
    MODEL_ID = os.getenv("MODEL_ID")

    # Generate timestamped output path
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = f"report/news_report_{timestamp}.pdf"

    # Initialize analyzer and perform analysis
    analyzer = BrandJournalistAnalyzer(api_key=API_KEY)
    response = analyzer._load_or_search(force_refresh=False)
    #response = analyzer.search_news()
    search_data = pd.DataFrame(response)

    # Extract storytelling and conclusion
    storytelling = analyzer.get_storytelling(response)
    conclusion  = analyzer.get_conclusion(response)

    # Generate visualizations
    visualizer = DataVisualizer(dataset=search_data)
    visualizer.plot_news_by_source()
    visualizer.plot_news_over_time()
    visualizer.plot_sentiment_category_heatmap()

    # Create PDF report
    report = ReportAnalysis(
        dataset=search_data,
        filename=output_path,
        conclusion=conclusion,
        storytelling=storytelling,
    )
    report.create_report()
    
