import time

from scraper import crawl_page, scrape_pages, scrape_page, scrape_pages_threaded, scrape_pages_async_thread
import asyncio
import concurrent.futures

import matplotlib.pyplot as plt

from db import get_client, uri

def plot_time_profiles(recorded_time: list[float]) -> None:
    fig, ax = plt.subplots()

    category = ["Sync", "Threading", "Async","Async with threading"]
    bar_labels = ["red", "blue", "orange","green"]
    bar_colors = ["tab:red", "tab:blue", "tab:orange","tab:green"]

    ax.bar(category, recorded_time, label=bar_labels, color=bar_colors)

    ax.set_ylabel("Execution time (in secs)")
    ax.set_title("Sync vs Threading vs Async execution time vs async+thread")
    ax.legend(title="Approach")
    plt.show()


async def main(urls):
    start_time = time.perf_counter()
    results = await asyncio.gather(
        *[scrape_pages(url) for url in urls]
    )  # creating 50 co-routines
    total_time = time.perf_counter() - start_time
    return results, total_time


async def main2(urls):
    start_time = time.perf_counter()

    # Threading
    async def threaded_scrape():
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            jobs = [executor.submit(scrape_pages_async_thread, url) for url in urls]
            return await asyncio.gather(*jobs)

    results = await threaded_scrape()

    total_time = time.perf_counter() - start_time
    return results, total_time


if __name__ == "__main__":
    # urls_found = crawl_page("https://www.imdb.com/chart/top")
    urls_found = [
        f"https://books.toscrape.com/catalogue/page-{idx}.html" for idx in range(1, 5)
    ]
    content = []
    times_taken = []

    # # Sync start
    start = time.perf_counter()
    for url in urls_found:
        content.append(scrape_page(url))
    sync_time = time.perf_counter() - start
    print(f"Sync took {sync_time} secs")
    times_taken.append(sync_time)
    # # # Sync end

     # Threading start
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        jobs = {
            executor.submit(scrape_pages_threaded, urls_found[idx : idx + 10]): idx
            for idx in range(0, len(urls_found), 10)
        }
        for job in concurrent.futures.as_completed(jobs):
            try:
                data = job.result()
                print(len(data))
            except Exception as exc:
                print("Failed to run job", exc)
    threading_time = time.perf_counter() - start
    print(f"Threading took {threading_time} secs")
    times_taken.append(threading_time)
    # Threading end

    # Async start
    res, async_time = asyncio.run(main(urls_found))
    print(f"Async took {async_time} secs")
    times_taken.append(async_time)
    # Async end



    #Async thread start

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        jobs = {
            executor.submit(scrape_pages_async_thread, urls_found[idx: idx + 10]): idx
            for idx in range(0, len(urls_found), 10)
        }
        for job in concurrent.futures.as_completed(jobs):
            data = job.result()

    res, async_time = asyncio.run(main(urls_found))
    print(f"Async with threading took {async_time} secs")
    times_taken.append(async_time)

    #Async thread end

    plot_time_profiles(times_taken)

    # DB writing start
    client = get_client()
    db = client.bruno
    collection = db.books_data
    collection.insert_many(res)
    # DB writing end
