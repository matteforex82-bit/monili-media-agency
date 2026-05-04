# Nano Banana 2 Product Prompt Knowledge

Use this knowledge for image-to-image product photography and product editing prompts.

## Core Prompt Structure
Every image prompt must be organized around these sections, even when written as one natural paragraph:
- Reference fidelity: what must remain identical from the uploaded product image.
- Scene / environment: where the product is placed or worn.
- Lighting: type, direction, softness, temperature and reflection control.
- Camera / lens: shot type, focal length, framing and depth of field.
- Styling & props: model, hand, outfit, supports, boutique props and palette.
- Format / output: Instagram feed 1:1, story 9:16, carousel slide, Google Business photo.
- Constraints: what must not change or appear.

## Reference Fidelity
- The uploaded product photo is the master image and source of truth.
- Preserve exact shape, size, color, material, proportions, stone count, metal finish, stitching, texture, pattern, closures and distinctive details.
- Do not add, remove, resize or redesign stones, charms, sleeves, collars, handles, patterns, logos, labels or closures.
- Do not turn the product into a different item.
- For jewelry, preserve stone cut, setting, prongs, band thickness, metal tone and scale.
- For clothing, preserve fabric, drape, length, neckline, sleeves, pattern, color and fit.

## Photorealism
- Ask for a real commercial still photo, natural optics, believable lens perspective, realistic shadows and physically plausible reflections.
- Prefer natural daylight, soft window light, softbox boutique lighting, warm shop lighting, or golden hour only when appropriate.
- Specify reflection control for gems and metals: highlight sparkle without burning detail.
- Avoid CGI shine, fantasy jewelry, waxy skin, over-smoothed faces, plastic hands, cartoon effects, fake luxury catalog look and 3D render aesthetics.
- Use realistic skin texture, correct hand anatomy, natural body proportions and believable garment behavior.

## Composition
- One clear hero subject. The product must be the main focus.
- Background can be invented, but must stay believable: Italian boutique, Ravenna-inspired street, warm fitting room, cafe table, linen flat lay, glass display case.
- Remove visual clutter. Do not let props compete with the product.
- Use controlled depth of field, focused product details and soft background blur.
- Do not use readable text in the image unless explicitly requested.
- Avoid phones, chat screens, fake websites, fake brand signs, fake packaging labels, random symbols, watermarks and logos.

## Product-Specific Direction
- Ring: show either a realistic hand try-on, premium macro, or elegant still life. Keep ring scale believable and do not add other rings.
- Earrings: show a realistic adult model, ear visible, hair away from the earring, light makeup, no competing earrings.
- Necklace: show bust-to-neck crop, simple clothing, chain length and pendant layout faithful to reference.
- Clothing: show the garment worn by a realistic adult model, full outfit context, natural pose, correct fabric drape and no design changes.
- Bags/accessories: show scale by hand/shoulder/table styling and one clean product hero.

## Output Roles
- Instagram feed: one finished publishable hero image, 1:1, no text overlay, no collage.
- Instagram story: vertical 9:16 image with clean negative space for text added later, no embedded text.
- Visual extras: exploratory commercial shots, different from carousel, no slide logic.
- Carousel: coherent 5-slide sequence; each slide has a different visual purpose but one unified campaign mood.
- Google Business: realistic boutique/local context, authentic and less editorial than Instagram.

## Useful Prompt Phrases
- "Using the uploaded image as the master product reference..."
- "Reference fidelity: preserve the exact product design, shape, proportions, color, material, stone placement and texture."
- "Lighting: soft directional light from 45 degrees, controlled reflections, no blown highlights."
- "Camera / lens: 70mm product photography lens, shallow depth of field, sharp focus on the product."
- "Format / output: finished Instagram feed photo, square 1:1, no text overlay."
- "Constraints: no readable text, no logos, no watermark, no phone screens, no fake UI, no extra jewelry competing with the product."

## Avoid
- Vague prompts like "make a beautiful product photo".
- Mixing visual styles such as photorealistic plus cartoon, watercolor or 3D render.
- Long negative-only prompts without a clear positive scene.
- Asking the model to generate text, labels, brand signs or chat screens inside the image.
- Reusing the same prompt role for feed, story, carousel and visual extras.
