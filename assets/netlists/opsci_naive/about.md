# Open Science Token Ecosystem
This simulation is testing the longevity of a decentralized open science ecosystem where researchers receive grants, buy data, and publish papers.

![](opsci_naive.jpeg)

### Description of one step in the loop

1. ```ResearcherAgent``` publishes a grant proposal (fixed price)
2. ```OCEANMinterAgent``` mints fixed amount of OCEAN and sends one part to ```RouterAgent``` (the amount for grant) and sells the rest to ```OCEANBurnerAgent```
3. ```OCEANBurnerAgent``` spends everything in its wallet
4. ```RouterAgent``` sends all OCEAN in wallet to ```ResearcherAgent```
5. ```ResearcherAgent``` sends fixed amount of OCEAN to ```MarketplaceAgent``` and the rest is burned (work done)
6. ```MarketplaceAgent``` sends all OCEAN evenly to all instances of ```SellerAgent```
7. ```ResearcherAgent``` "publishes" research to ```MarketplaceAgent``` (corresponding to ```data += 1```)
8. New ```SellerAgent``` is created (corresponding to a researcher selling data from research)

