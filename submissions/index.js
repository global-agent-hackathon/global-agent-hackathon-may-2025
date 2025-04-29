import cron from 'node-cron';
import fetch from 'node-fetch';
import dotenv from 'dotenv';

dotenv.config();

const { FETCH_NEWS_API_URL, POST_NEWS_API_URL, FETCH_PUZZLE_API_URL, POST_PUZZLE_API_URL } = process.env;

// Define the scheduled job
cron.schedule('*/2 * * * *', async () => {
  console.log(`[${new Date().toISOString()}] News Cron job started`);

  try {
    // Step 1: Fetch data from API A
    const fetchResponse = await fetch(FETCH_NEWS_API_URL);
    
    if (!fetchResponse.ok) {
      throw new Error(`Fetch API failed with status ${fetchResponse.status}`);
    }
    
    const data = await fetchResponse.json();
    console.log('Fetched data:', data);
    const postData = {}
    postData.title = data.title
    postData.description = data.description
    postData.sourceLinks = data.source_links
    postData.translations = data.translations

    console.log('Post data:', postData);

    // Step 2: Send data to API B
    const postResponse = await fetch(POST_NEWS_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData),
    });

    if (!postResponse.ok) {
      throw new Error(`Post API failed with status ${postResponse.status}`);
    }

    console.log('Successfully posted data to API B');

  } catch (error) {
    console.error(`[${new Date().toISOString()}] Error occurred:`, error.message);
  }
});

cron.schedule('* * * * *', async () => {
  console.log(`[${new Date().toISOString()}] Puzzle Cron job started`);

  try {
    // Step 1: Fetch data from API C
    const fetchResponse = await fetch(FETCH_PUZZLE_API_URL);
    
    if (!fetchResponse.ok) {
      throw new Error(`Fetch Puzzle API failed with status ${fetchResponse.status}`);
    }
    
    const data = await fetchResponse.json();
    console.log('Fetched puzzle data:', data);

    console.log('Post data:', data);

    // Step 2: Send data to API D
    const postResponse = await fetch(POST_PUZZLE_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!postResponse.ok) {
      throw new Error(`Post puzzle API failed with status ${postResponse.status}`);
    }

    console.log('Successfully posted data to API D');

  } catch (error) {
    console.error(`[${new Date().toISOString()}] Error occurred:`, error.message);
  }
});

console.log('Cron worker started and running...');