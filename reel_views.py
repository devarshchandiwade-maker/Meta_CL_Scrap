import instaloader

L = instaloader.Instaloader()

# Reel shortcode
SHORTCODE = "DUfKbuzjd16"

post = instaloader.Post.from_shortcode(
    L.context,
    SHORTCODE
)

print("Views:", post.video_view_count)
print("Likes:", post.likes)
print("Comments:", post.comments)
print("Caption:", post.caption)