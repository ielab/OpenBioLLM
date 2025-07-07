import urllib.request
import urllib.error
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

def call_api(url, max_retries=3):
	# Set maximum retries to avoid infinite retries
	retry_count = 0
	time.sleep(1)
	url = url.replace(' ', '+')

	while retry_count < max_retries:
		try:
			logger.info(f"Calling API with URL: {url}")
			req = urllib.request.Request(url)
			with urllib.request.urlopen(req) as response:
				call = response.read()
			return call
		except urllib.error.HTTPError as e:
			# If HTTP 500 error, retry
			if e.code == 500:
				retry_count += 1
				logger.warning(f"HTTP 500 Error encountered. Retry {retry_count}/{max_retries}...")
				time.sleep(5)  # Wait 5 seconds before retrying
			else:
				# For other errors, record and return None
				logger.error(f"Error calling API with URL: {url}")
				logger.error(f"Exception: {str(e)}", exc_info=True)
				return None
		except Exception as e:
			logger.error(f"Error calling API with URL: {url}")
			logger.error(f"Exception: {str(e)}", exc_info=True)
			return None

	# If retries are exhausted, return None
	logger.error(f"API call failed after {max_retries} attempts.")
	return None