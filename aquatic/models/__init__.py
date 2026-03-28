# aquatic/models/__init__.py

# 1. 個人檔案與路徑
# 2. 商業魚隻與路徑
from .aquatic_life_img import AquaticImage, AquaticLife, get_aquatic_upload_path

# 3. 寵物魚與路徑
from .aquatic_life_img_pet import PetFish, get_pet_upload_path

# 4. 社交文章與路徑
from .post_comment import Comment, Post, get_blog_upload_path
from .profile import Profile, get_profile_upload_path

# 5. 其他
from .shop_notice import ShopNotice

# models 資料夾的入口只能放「模型（Class）」，不能放「工具（函式）」
