# PARTY FOX
This code has been ported over from a private repo as an example of my work - RD

## Description
This site was created for a company running online children's parties during the covid lockdowns lockdown. This is quite a complex booking system in which the person booking it enters other parents' email addresses, who can then fill in details about their own child online using an emailed access token.

This was a solo project; I was the only dev and designer, although the frontend was built to a comprehensive requirements doc. The project was also a chance to try out a different tech stack.

## Tech Stack
* **Frontend**: Svelte JS (looking for something more lightweight than Vue - see ./src)
* **Backend**: Chalice on AWS Lambda (testing easy Python deployments on AWS - ./backend)
* **DB**: DynamoDB (single table design - wanted to experiment with access patterns)
* **APIs**: Taking payments with Stripe, sending transactional email with Mailgun

## Status
Now we are out of lockdown the company is no longer running the parties and the site is offline. I have anonymised some of the assets in the repo.
