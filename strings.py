# All bot messages in Uzbek

GAME_ALREADY_RUNNING = "⚠️ Bu guruhda o'yin allaqachon boshlanmoqda!"
GAME_NOT_RUNNING = "⚠️ Hozir faol o'yin yo'q. /newgame bilan boshlang."
GAME_STARTED_LOBBY = (
    "🎭 *Mafia o'yini boshlanmoqda!*\n\n"
    "Qo'shilish uchun /join bosing.\n"
    "Kamida {min_players} ta o'yinchi kerak.\n\n"
    "O'yin boshlagich: {host}"
)
ALREADY_JOINED = "⚠️ Siz allaqachon o'yinga qo'shilgansiz!"
JOINED = "✅ *{name}* o'yinga qo'shildi! Jami: {count} o'yinchi."
NOT_ENOUGH_PLAYERS = "⚠️ Kamida {min_players} ta o'yinchi kerak. Hozir: {count} ta."
ONLY_ADMIN_CAN_START = "⚠️ Faqat guruh admini o'yinni boshlay oladi."
GAME_CANCELLED = "❌ O'yin bekor qilindi."
ONLY_ADMIN_CAN_CANCEL = "⚠️ Faqat guruh admini o'yinni bekor qila oladi."
NOT_IN_GAME = "⚠️ Siz bu o'yinda yo'qsiz."
NO_GAME_TO_CANCEL = "⚠️ Bekor qilish uchun faol o'yin yo'q."

ROLES_ASSIGNED = (
    "🎭 *O'yin boshlanmoqda!*\n\n"
    "Rollar tayinlandi. Har bir o'yinchi o'z rolini xususiy xabarda oldi.\n\n"
    "*O'yinchilar:*\n{players}"
)

YOUR_ROLE_MAFIA = (
    "🔴 *Sizning rolingiz: MAFIYA*\n\n"
    "Siz mafiyasiz! Har kecha bir fuqaroni o'ldirasiz.\n"
    "Guruh chatda oddiy fuqarodek ko'rinsangiz.\n\n"
    "*Mafiya a'zolari:* {teammates}"
)
YOUR_ROLE_DOCTOR = (
    "💚 *Sizning rolingiz: DOKTOR*\n\n"
    "Siz doktorsiz! Har kecha bir o'yinchini saqlab qolasiz.\n"
    "O'zingizni ham saqlay olasiz (faqat bir marta)."
)
YOUR_ROLE_SHERIFF = (
    "🔵 *Sizning rolingiz: SHERIF*\n\n"
    "Siz sherifisiz! Har kecha bir o'yinchini tekshirasiz.\n"
    "Bot sizga u mafiyami yoki yo'qligini aytadi."
)
YOUR_ROLE_CITIZEN = (
    "⚪ *Sizning rolingiz: FUQARO*\n\n"
    "Siz oddiy fuqarosiz! Maxsus qobilyatingiz yo'q.\n"
    "Kunduz kuni ovoz berish orqali mafiyani toping."
)

NIGHT_START = (
    "🌙 *TUN BOSHLANDI — {round}-tur*\n\n"
    "Hamma uxlamoqda... Mafiya harakat qilyapti.\n"
    "O'z rollaringizga ko'ra xususiy xabarda harakat qiling."
)
NIGHT_MAFIA_CHOOSE = (
    "🔴 *Mafiya, kim o'lsin?*\n\n"
    "Qurbon tanlang:"
)
NIGHT_DOCTOR_CHOOSE = (
    "💚 *Doktor, kimni davolaysiz?*\n\n"
    "Saqlamoqchi bo'lgan o'yinchini tanlang:"
)
NIGHT_SHERIFF_CHOOSE = (
    "🔵 *Sherif, kimni tekshirasiz?*\n\n"
    "Tekshirmoqchi bo'lgan o'yinchini tanlang:"
)

SHERIFF_RESULT_MAFIA = "🔴 *{name}* — bu MAFIYA!"
SHERIFF_RESULT_CLEAN = "✅ *{name}* — bu oddiy fuqaro."

NIGHT_ACTION_RECORDED = "✅ Tanlovingiz qabul qilindi."
ALREADY_ACTED = "⚠️ Siz allaqachon harakat qildingiz."

DAY_START_KILLED = (
    "☀️ *KUN BOSHLANDI — {round}-tur*\n\n"
    "😢 Kecha *{name}* o'ldirildi.\n\n"
    "60 soniya muhokama qiling, keyin ovoz berish boshlanadi."
)
DAY_START_SAVED = (
    "☀️ *KUN BOSHLANDI — {round}-tur*\n\n"
    "🍀 Kecha hech kim o'lmadi — doktor kimnidir saqlab qoldi!\n\n"
    "60 soniya muhokama qiling, keyin ovoz berish boshlanadi."
)

VOTE_START = (
    "🗳️ *OVOZ BERISH BOSHLANMOQDA!*\n\n"
    "Kim o'yindan chiqsin? Tanlang:"
)
VOTE_SKIP = "⏭️ Hech kimni chiqarmaslik"
VOTE_RECORDED = "✅ Ovozingiz qabul qilindi."
ALREADY_VOTED = "⚠️ Siz allaqachon ovoz berdingiz."
VOTE_RESULT_ELIMINATED = (
    "🗳️ *Ovoz berish natijasi:*\n\n"
    "😵 *{name}* o'yindan chiqarildi! (Roli: {role})\n"
)
VOTE_RESULT_TIE = (
    "🗳️ *Ovoz berish natijasi:*\n\n"
    "🤝 Durang! Hech kim o'yindan chiqarilmadi.\n"
)
VOTE_RESULT_SKIP = (
    "🗳️ *Ovoz berish natijasi:*\n\n"
    "⏭️ O'yinchilar hech kimni chiqarmaslikni tanladi.\n"
)

WIN_CITIZENS = (
    "🎉 *FUQAROLAR YUTDI!*\n\n"
    "Barcha mafiya a'zolari topildi va o'yindan chiqarildi.\n\n"
    "*O'yinchilar ro'yxati:*\n{summary}"
)
WIN_MAFIA = (
    "💀 *MAFIYA YUTDI!*\n\n"
    "Mafiya fuqarolarni yengdi!\n\n"
    "*O'yinchilar ro'yxati:*\n{summary}"
)

PLAYER_DEAD_CANNOT_ACT = "☠️ Siz o'yindan chiqgansiz va harakat qila olmaysiz."
GAME_NOT_IN_NIGHT = "⚠️ Hozir tun fazasi emas."
GAME_NOT_IN_VOTE = "⚠️ Hozir ovoz berish fazasi emas."

ALIVE_PLAYERS = "*Tirik o'yinchilar ({count}):*\n{list}"
