import streamlit as st

#Unterseiten
def render_detail_page(doc, q):
    title = doc["title"][0]
    description = doc["description"][0] if doc["description"] else "no data"
    genres = doc["genres"] if doc["genres"] else []
    publisher = doc["publisher"] if doc["publisher"] else []
    platforms = doc["platforms"] if doc["platforms"] else []
    image_url = doc["image"][0] if doc["image"] else ""
    url = doc["url"][0] if doc["url"] else "no data"
    trailer = doc["trailer"][0] if doc["trailer"] else None
    date = doc["release_date"][0] if doc["release_date"] else "no data"

    if publisher is not None:
       publisher_html = "<div>"
       for tag in publisher:
           publisher_html += f'<span class="tag">{tag}</span>'
       publisher_html += "</div>"
    
    if genres is not None:
       genre_html = "<div>"
       for tag in genres:
           genre_html += f'<span class="tag">{tag}</span>'
       genre_html += "</div>"
    
    if platforms is not None:
       platform_html = "<div>"
       for tag in platforms:
           platform_html += f'<span class="tag">{tag}</span>'
       platform_html += "</div>"

    if st.button("Back to overview"):
        st.query_params.update({"view": "grid", "q": q})
        st.query_params.pop("id", None)
        st.rerun()

    st.title(title)

    video_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embedded Video Player</title>
    <link href="https://vjs.zencdn.net/8.5.2/video-js.css" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 99vh;
            background: #000;
        }}
        .video-js {{
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
<script src="https://vjs.zencdn.net/8.5.2/video.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<video id="video-player" class="video-js vjs-default-skin" controls preload="auto">
        <track id="subtitle-track" kind="subtitles" label="English" srclang="en" default>
</video>
<script>
const player = videojs('video-player', {{
            autoplay: true,
            muted: false,
            controls: true,
            preload: 'auto',
            playbackRates: [0.5, 1, 1.5, 2],
            fluid: false,
            crossOrigin: 'anonymous',
        }});
if (Hls.isSupported()) {{
            player.src({{
                src: "{trailer}",
                type: 'application/x-mpegURL'
            }});
        }} else {{
            alert('Your browser does not support HLS playback.');
        }}
</script>
</body>
</html>""".replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;').replace("'","&#039;")
                
    html = ['<div class="layout">']

    if trailer is not None:
        iframe = f'<iframe class="trailer" srcdoc="{video_html}" allow="accelerometer; ambient-light-sensor; autoplay; battery; camera; clipboard-write; document-domain; encrypted-media; fullscreen; geolocation; gyroscope; layout-animations; legacy-image-formats; magnetometer; microphone; midi; oversized-images; payment; picture-in-picture; publickey-credentials-get; sync-xhr; usb; vr ; wake-lock; xr-spatial-tracking"></iframe>'
    else:
        iframe = f'<img src="{image_url}" loading="lazy" alt="poster">' if image_url else ""

    if url == "no data":
        web_url = f'<p class="link">{url}</p>'
    else:
        web_url = f'<a class="link" href="{url}"><p>{url}</p></a>'

    html.append(f'<div class="column_l">{iframe}<p>{description}</p></div>')
    html.append(f'<div class="column_r"><p>Genres:</p><p>{genre_html}</p><p>Publisher:</p><p>{publisher_html}</p><p>Available for platforms:</p><p>{platform_html}</p><p>Website:</p>{web_url}<p>Date:</p><p>{date}</p></div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

    st.stop()