import FirecrawlApp from '@mendable/firecrawl-js';

interface CrawlResult {
  url: string;
  markdown: string;
  title?: string;
  description?: string;
}

class FirecrawlService {
  private app: FirecrawlApp;

  constructor(apiKey?: string) {
    if (!apiKey) {
      throw new Error('Firecrawl API key is required. Please set your API key.');
    }
    this.app = new FirecrawlApp({ apiKey });
  }

  async scrapeUrl(url: string): Promise<CrawlResult> {
    try {
      const result = await this.app.scrapeUrl(url, {
        formats: ['markdown'],
        onlyMainContent: true
      });

      if (!result || !result.markdown) {
        throw new Error('Failed to scrape content from the URL');
      }

      return {
        url: result.url || url,
        markdown: result.markdown,
        title: result.metadata?.title,
        description: result.metadata?.description
      };
    } catch (error: any) {
      console.error('Error scraping URL:', error);
      throw new Error(`Failed to crawl URL: ${error.message || 'Unknown error'}`);
    }
  }

  async crawlWebsite(url: string, maxPages: number = 10): Promise<CrawlResult[]> {
    try {
      const crawlResult = await this.app.crawlUrl(url, {
        limit: maxPages,
        scrapeOptions: {
          formats: ['markdown'],
          onlyMainContent: true
        }
      });

      if (!crawlResult || !crawlResult.data) {
        throw new Error('Failed to crawl website');
      }

      return crawlResult.data.map((item: any) => ({
        url: item.url,
        markdown: item.markdown || '',
        title: item.metadata?.title,
        description: item.metadata?.description
      }));
    } catch (error: any) {
      console.error('Error crawling website:', error);
      throw new Error(`Failed to crawl website: ${error.message || 'Unknown error'}`);
    }
  }
}

export { FirecrawlService, type CrawlResult }; 