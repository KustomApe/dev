import pynder
session = pynder.Session('Facebookのアクセストークン')
friends = session.get_fb_friends()

#緯度と経度を指定
# Yokohama Station
LAT = 35.465786
LON = 139.622313

session.update_location(LAT, LON)
session.profile
users = session.nearby_users()
for user in users:
    print(user.name)
    print(user.schools)
    print(user.distance_km)
    print(user.instagram_username)
    print(user.common_connections)
    print("============")