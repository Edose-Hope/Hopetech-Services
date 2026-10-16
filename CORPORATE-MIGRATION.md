# Hopetech corporate and solar website transition

Prepared structure:

- `corporate/`: new company homepage, stylesheet, script, local fonts and assets.
- `solar/`: a copy of the existing solar website, including images, products and the existing Formspree contact form. Canonicals and sitemap use `https://solar.hopetechservices.com.ng`. Solar navigation links back to the corporate website.
- Existing root solar files are deliberately unchanged until hosting and domain routing are confirmed.
- Training remains its independent, working Vercel project at `https://training.hopetechservices.com.ng`. No training application or database files were changed by this work.

## Confirm the hosting first

Whogohost may be only the domain registrar. Check the active services in the Whogohost client area. If hosting is listed, open cPanel → File Manager and find the document root for `hopetechservices.com.ng`. Confirm that its `index.html` is the current solar website before uploading anything. If only a domain is listed, identify the host from the DNS records and hosting account before proceeding. Do not change nameservers or the existing training CNAME.

## cPanel cutover, if this is the confirmed live host

1. Download a backup of the complete live document root and save it outside any publicly accessible directory. Preserve the existing `.htaccess`, ownership-verification files, mail configuration and other unrelated files.
2. In cPanel → Domains, create `solar.hopetechservices.com.ng` with a separate document root, typically `public_html/solar`. Do not share the main domain's document root. Confirm the actual path displayed by cPanel.
3. Extract the contents of the solar upload archive into that document root. The archive contains `index.html` directly; do not accidentally create an extra nested `solar` directory.
4. Check the authoritative DNS zone. If cPanel has not created the subdomain record there, add the record supplied by the confirmed web host. For cPanel hosting this is commonly an A record named `solar` pointing to that account's actual server IP. Use the IP shown by the host, not an assumed Vercel address. Leave root, email and training records alone.
5. Run/allow AutoSSL for the new solar domain. Check HTTPS, navigation, product images and the contact form on `https://solar.hopetechservices.com.ng/`. Submit a form only when the owner wants a real enquiry sent.
6. Only after the solar subdomain works, extract the corporate upload archive into the main domain's document root. Its files replace the root `index.html` and add `corporate.css`, `corporate.js` and `assets/`. Back up any colliding `assets` directory first and merge rather than delete unrelated files. Check DirectoryIndex if an older `index.php` would take precedence.
7. Confirm main-domain navigation reaches the solar subdomain and the existing training subdomain. Confirm mail links, phone links, mobile menu, logo and favicon. Purge the hosting cache if necessary.
8. Redirect old solar page URLs after the move. Merge these rules into the existing root `.htaccess` in the appropriate place; do not overwrite the entire file:

```apache
RewriteEngine On
RewriteCond %{HTTP_HOST} ^(www\.)?hopetechservices\.com\.ng$ [NC]
RewriteRule ^(about\.html|services-full\.html|thanks\.html)$ https://solar.hopetechservices.com.ng/$1 [R=301,L]
```

The new main-domain sitemap lists the corporate homepage. The solar sitemap lists solar pages. Keep the existing Google ownership-verification file at the main domain.

## If the host is Vercel or another service

Do not follow cPanel upload steps. Configure a separate solar project/domain (or host-based routing), deploy the solar directory there, verify its domain and certificate, and then deploy the corporate directory for the main domain. The same solar-first order applies. Use the exact DNS values given by that host.

## Rollback

Restore the backed-up main document root if the corporate cutover fails. Leave the working training CNAME unchanged. The original root solar files remain in Git as a second source of the original site, but the live backup is authoritative if it contains changes not committed here.

## Editing

This corporate homepage is a static website. The existing training dashboard edits the training website only; it does not edit these corporate or solar files.

## Local verification

From this repository, `python -m http.server 8091 --bind 127.0.0.1` serves `/corporate/` and `/solar/` for development. The corporate preview intentionally links to `/solar/` on the same host. The production corporate archive sets `data-solar-url="https://solar.hopetechservices.com.ng/"` and uses that live subdomain in all solar links. No localhost preview URLs should be shared with the owner.
