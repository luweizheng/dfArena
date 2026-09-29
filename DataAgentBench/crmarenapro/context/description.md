# crmarenapro

The six original data groups are provided as local Parquet tables.

The original group names are retained. File paths below are relative to the dataset root.

## core_crm

This database is provided as Parquet tables and contains core CRM data including users, accounts, and contacts from Salesforce CRMArena. This database consists of three tables.

### User

Sales team information

File: `data/core_crm/User.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `FirstName` | string |
| `LastName` | string |
| `Email` | string |
| `Phone` | string |
| `Username` | string |
| `Alias` | string |
| `LanguageLocaleKey` | string |
| `EmailEncodingKey` | string |
| `TimeZoneSidKey` | string |
| `LocaleSidKey` | string |

### Account

Company/customer data

File: `data/core_crm/Account.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `Name` | string |
| `Phone` | string |
| `Industry` | string |
| `Description` | string |
| `NumberOfEmployees` | double |
| `ShippingState` | string |

### Contact

Individual contacts

File: `data/core_crm/Contact.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `FirstName` | string |
| `LastName` | string |
| `Email` | string |
| `AccountId` | string |

## sales_pipeline

This database is provided as Parquet tables and contains sales pipeline data including opportunities, quotes, contracts, and leads. This database consists of six tables.

### Contract

Signed contracts

File: `data/sales_pipeline/Contract.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `AccountId` | string |
| `Status` | string |
| `StartDate` | string |
| `CustomerSignedDate` | string |
| `CompanySignedDate` | string |
| `Description` | string |
| `ContractTerm` | string |

### Lead

Sales leads

File: `data/sales_pipeline/Lead.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `FirstName` | string |
| `LastName` | string |
| `Email` | string |
| `Phone` | string |
| `Company` | string |
| `Status` | string |
| `ConvertedContactId` | string |
| `ConvertedAccountId` | string |
| `Title` | string |
| `CreatedDate` | string |
| `ConvertedDate` | string |
| `IsConverted` | int64 |
| `OwnerId` | string |

### Opportunity

Sales deals

File: `data/sales_pipeline/Opportunity.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `ContractID__c` | string |
| `AccountId` | string |
| `ContactId` | string |
| `OwnerId` | string |
| `Probability` | string |
| `Amount` | double |
| `StageName` | string |
| `Name` | string |
| `Description` | string |
| `CreatedDate` | string |
| `CloseDate` | string |

### OpportunityLineItem

Deal line items

File: `data/sales_pipeline/OpportunityLineItem.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `OpportunityId` | string |
| `Product2Id` | string |
| `PricebookEntryId` | string |
| `Quantity` | string |
| `TotalPrice` | string |

### Quote

Price quotes

File: `data/sales_pipeline/Quote.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `OpportunityId` | string |
| `AccountId` | string |
| `ContactId` | string |
| `Name` | string |
| `Description` | string |
| `Status` | string |
| `CreatedDate` | string |
| `ExpirationDate` | string |

### QuoteLineItem

Quote details

File: `data/sales_pipeline/QuoteLineItem.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `QuoteId` | string |
| `OpportunityLineItemId` | string |
| `Product2Id` | string |
| `PricebookEntryId` | string |
| `Quantity` | string |
| `UnitPrice` | string |
| `Discount` | string |
| `TotalPrice` | string |

## support

This database is provided as Parquet tables and contains customer support data including cases, knowledge articles, and communications. This database consists of six tables.

### Case

Support cases

File: `data/support/Case.parquet`

| Column | Arrow type |
|---|---|
| `id` | string |
| `priority` | string |
| `subject` | string |
| `description` | string |
| `status` | string |
| `contactid` | string |
| `createddate` | string |
| `closeddate` | string |
| `orderitemid__c` | string |
| `issueid__c` | string |
| `accountid` | string |
| `ownerid` | string |

### knowledge__kav

Knowledge articles

File: `data/support/knowledge__kav.parquet`

| Column | Arrow type |
|---|---|
| `id` | string |
| `title` | string |
| `faq_answer__c` | string |
| `summary` | string |
| `urlname` | string |

### issue__c

Custom issues

File: `data/support/issue__c.parquet`

| Column | Arrow type |
|---|---|
| `id` | string |
| `name` | string |
| `description__c` | string |

### casehistory__c

Case history

File: `data/support/casehistory__c.parquet`

| Column | Arrow type |
|---|---|
| `id` | string |
| `caseid__c` | string |
| `oldvalue__c` | string |
| `newvalue__c` | string |
| `createddate` | string |
| `field__c` | string |

### emailmessage

Email communications

File: `data/support/emailmessage.parquet`

| Column | Arrow type |
|---|---|
| `id` | string |
| `subject` | string |
| `textbody` | string |
| `parentid` | string |
| `fromaddress` | string |
| `toids` | string |
| `messagedate` | string |
| `relatedtoid` | string |

### livechattranscript

Chat logs

File: `data/support/livechattranscript.parquet`

| Column | Arrow type |
|---|---|
| `id` | string |
| `caseid` | string |
| `accountid` | string |
| `ownerid` | string |
| `body` | string |
| `endtime` | string |
| `livechatvisitorid` | string |
| `contactid` | string |

## products_orders

This database is provided as Parquet tables and contains product catalog and order data. This database consists of seven tables.

### ProductCategory

Product categories

File: `data/products_orders/ProductCategory.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `Name` | string |
| `CatalogId` | string |

### Product2

Product catalog

File: `data/products_orders/Product2.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `Name` | string |
| `Description` | string |
| `IsActive` | int64 |
| `External_ID__c` | string |

### ProductCategoryProduct

one of the pricing and mapping tables

File: `data/products_orders/ProductCategoryProduct.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `ProductCategoryId` | string |
| `ProductId` | string |

### Pricebook2

one of the pricing and mapping tables

File: `data/products_orders/Pricebook2.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `Name` | string |
| `Description` | string |
| `IsActive` | int64 |
| `ValidFrom` | string |
| `ValidTo` | string |

### PricebookEntry

one of the pricing and mapping tables

File: `data/products_orders/PricebookEntry.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `Pricebook2Id` | string |
| `Product2Id` | string |
| `UnitPrice` | string |

### Order

Customer orders

File: `data/products_orders/Order.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `AccountId` | string |
| `Status` | string |
| `EffectiveDate` | string |
| `Pricebook2Id` | string |
| `OwnerId` | string |

### OrderItem

Order details

File: `data/products_orders/OrderItem.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `OrderId` | string |
| `Product2Id` | string |
| `Quantity` | string |
| `UnitPrice` | string |
| `PriceBookEntryId` | string |

## activities

This database is provided as Parquet tables and contains activity data including tasks, events, and voice call transcripts. This database consists of three tables.

### Event

Calendar events

File: `data/activities/Event.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `WhatId` | string |
| `OwnerId` | string |
| `StartDateTime` | string |
| `Subject` | string |
| `Description` | string |
| `DurationInMinutes` | string |
| `Location` | string |
| `IsAllDayEvent` | int64 |

### Task

Activities and tasks

File: `data/activities/Task.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `WhatId` | string |
| `OwnerId` | string |
| `Priority` | string |
| `Status` | string |
| `ActivityDate` | string |
| `Subject` | string |
| `Description` | string |

### VoiceCallTranscript__c

Call records

File: `data/activities/VoiceCallTranscript__c.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `OpportunityId__c` | string |
| `LeadId__c` | string |
| `Body__c` | string |
| `CreatedDate` | string |
| `EndTime__c` | string |

## territory

This database is provided as Parquet tables and contains sales territory management data. This database consists of two tables.

### Territory2

Sales territories

File: `data/territory/Territory2.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `Name` | string |
| `Description` | string |

### UserTerritory2Association

Territory assignments

File: `data/territory/UserTerritory2Association.parquet`

| Column | Arrow type |
|---|---|
| `Id` | string |
| `UserId` | string |
| `Territory2Id` | string |

## Representation

In the support group, physical table and column names are lowercase except for the table "Case", whose capital C is significant. Numeric-looking and date-looking text is stored as text; NumberOfEmployees and Amount are float64.
