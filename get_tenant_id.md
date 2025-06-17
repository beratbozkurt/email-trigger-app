# How to get your Tenant ID

1. Go to Azure Portal → Azure Active Directory
2. In the Overview page, copy the "Tenant ID" 
3. It looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
4. Replace `OUTLOOK_TENANT_ID=common` with `OUTLOOK_TENANT_ID=your-tenant-id`

OR

Make your app multi-tenant in Azure Portal:
- App Registration → Authentication → Supported account types → Multi-tenant + personal accounts