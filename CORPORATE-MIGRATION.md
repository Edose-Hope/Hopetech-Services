# Temporary coming-soon mode

The owner requested that the main corporate website remain unpublished. The build now publishes `corporate/coming-soon.html` as the main homepage and excludes the full corporate homepage, scripts and stylesheet from the public output. The full corporate source remains in Git for future launch. The coming-soon page links only to the energy business and the company email; it has no training link. It requests noindex through its own metadata, without applying that instruction to energy. The energy hostname routing is unchanged. `/corporate/` and `/corporate/index.html` temporarily redirect to the coming-soon homepage. To launch the full corporate site later, explicitly change the build output and remove the temporary redirect.

The remaining notes describe the prepared corporate/energy structure.

# Corporate and solar websites on Vercel

The main company website and the solar division share the existing **Hopetech-Services** Vercel project. Training stays in its independent **hopetech-training** project and database.

| Domain | Content |
| --- | --- |
| `hopetechservices.com.ng` | New corporate homepage introducing both businesses |
| `energy.hopetechservices.com.ng` | Existing solar website, products and enquiry form |
| `training.hopetechservices.com.ng` | Existing training site and admin content editor |

## Build and routing

Run `node scripts/build-site.mjs`. It creates a static `dist/` with the corporate homepage, its assets, the solar site and the existing Google ownership verification file. PHP source, PHPMailer, Git metadata and migration documentation are excluded from the public output. Solar enquiries continue to use the existing Formspree endpoint; no new form service is introduced.

`vercel.json` declares the build command and output directory. Its domain routes run **before** the filesystem: requests to the solar hostname are served from `dist/solar/`, and the main hostname uses the corporate `dist/index.html`. This order matters: filesystem-first rewrites would serve the corporate homepage on both hostnames.

The corporate homepage links directly to the solar and training domains. Solar navigation links back to the corporate website. Legacy main-domain solar page URLs (`about.html`, `services-full.html`, `thanks.html`) redirect to equivalent pages on the solar domain. Solar canonicals and its sitemap use the solar domain; the corporate sitemap lists the main homepage.

The root source solar files remain in Git for preservation. Vercel serves only the explicit build output, so the old root source `index.html` is not the deployed main homepage.

## Domains and DNS

The user connected `solar.hopetechservices.com.ng`, then chose `energy.hopetechservices.com.ng` as the final address. Before deploying this cutover, add the energy domain to Production on the same Vercel project, create its CNAME in Whogohost using the exact value Vercel provides, and confirm **Valid Configuration** and HTTPS. Keep root, email and training records as configured. The prepared cutover redirects the older solar hostname to energy, preserving paths. Do not activate this redirect before the energy domain works.

Pushing this configuration triggers the existing Vercel production deployment. Verify that the deployment for the new commit is **Ready**, then check:

1. Main domain: corporate homepage, both business links, logo and mobile menu.
2. Solar domain: solar homepage, products, images, navigation and enquiry form.
3. Training domain: existing site, registration and admin editor.
4. Main-domain `/services-full.html`: redirect to the solar domain.
5. Both domains: HTTPS and appropriate canonical/sitemap URLs.

The Vercel alias `hopetech-services.vercel.app` serves the corporate homepage by default. The solar domain is not redirected to the corporate domain.

## Local verification

Use `node scripts/build-site.mjs` to verify the production static output. A basic file server previews `dist/`, but does not reproduce domain routing. Domain-routing checks must send the correct host header and evaluate the declared Vercel routes before resolving the files.

The corporate layout was checked at desktop, tablet and mobile widths. Browser checks covered images, mobile menu and navigation between the corporate and solar sites. The solar form was checked using an intercepted Formspree response; no real enquiry was sent. These local checks do not independently verify production deployment or certificates.

## Editing and rollback

The training admin dashboard edits training content only. Corporate and solar content live in this repository.

For rollback, use Vercel's previous production deployment or revert the cutover configuration. The original root solar files remain unchanged. Do not remove the working training domain or change its CNAME while rolling back this project.
