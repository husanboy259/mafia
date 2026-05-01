module.exports = {
  START: (channel) =>
    `👋 Salom! Bu botda <b>Mafia</b> o'yinini o'ynashingiz mumkin.\n\nO'yin faqat guruh chatda ishlaydi. Quyidagi kanalimizga qo'shiling:\n<a href="${channel}">${channel}</a>`,

  GAME_ALREADY_RUNNING: "⚠️ Bu guruhda o'yin allaqachon boshlanmoqda!",
  GAME_NOT_RUNNING: "⚠️ Hozir faol o'yin yo'q. /newgame bilan boshlang.",
  GROUP_ONLY: "Bu komanda faqat guruh chatda ishlaydi.",

  GAME_STARTED_LOBBY: (host, min) =>
    `🎭 *Mafia o'yini boshlanmoqda\\!*\n\nQo'shilish uchun /join bosing\\.\nKamida ${min} ta o'yinchi kerak\\.\n\nO'yin boshlagich: ${esc(host)}`,

  ALREADY_JOINED: "⚠️ Siz allaqachon o'yinga qo'shilgansiz!",
  JOINED: (name, count) => `✅ *${esc(name)}* o'yinga qo'shildi\\! Jami: ${count} o'yinchi\\.`,

  NOT_ENOUGH_PLAYERS: (min, count) =>
    `⚠️ Kamida ${min} ta o'yinchi kerak\\. Hozir: ${count} ta\\.`,

  ONLY_ADMIN_CAN_START: "⚠️ Faqat guruh admini o'yinni boshlay oladi.",
  ONLY_ADMIN_CAN_CANCEL: "⚠️ Faqat guruh admini o'yinni bekor qila oladi.",
  GAME_CANCELLED: "❌ O'yin bekor qilindi.",
  NO_GAME_TO_CANCEL: "⚠️ Bekor qilish uchun faol o'yin yo'q.",

  ROLES_ASSIGNED: (players) =>
    `🎭 *O'yin boshlanmoqda\\!*\n\nRollar tayinlandi\\. Har bir o'yinchi o'z rolini xususiy xabarda oldi\\.\n\n*O'yinchilar:*\n${players}`,

  YOUR_ROLE_MAFIA: (teammates) =>
    `🔴 *Sizning rolingiz: MAFIYA*\n\nSiz mafiyasiz\\! Har kecha bir fuqaroni o'ldirasiz\\.\n\n*Mafiya a'zolari:* ${esc(teammates)}`,
  YOUR_ROLE_DOCTOR:
    `💚 *Sizning rolingiz: DOKTOR*\n\nSiz doktorsiz\\! Har kecha bir o'yinchini saqlab qolasiz\\.\nO'zingizni ham saqlay olasiz \\(faqat bir marta\\)\\.`,
  YOUR_ROLE_SHERIFF:
    `🔵 *Sizning rolingiz: SHERIF*\n\nSiz sherifisiz\\! Har kecha bir o'yinchini tekshirasiz\\.\nBot sizga u mafiyami yoki yo'qligini aytadi\\.`,
  YOUR_ROLE_CITIZEN:
    `⚪ *Sizning rolingiz: FUQARO*\n\nSiz oddiy fuqarosiz\\! Maxsus qobilyatingiz yo'q\\.\nKunduz kuni ovoz berish orqali mafiyani toping\\.`,

  NIGHT_START: (round) =>
    `🌙 *TUN BOSHLANDI — ${round}\\-tur*\n\nHamma uxlamoqda\\.\\.\\. Mafiya harakat qilyapti\\.\nO'z rollaringizga ko'ra xususiy xabarda harakat qiling\\.`,

  NIGHT_MAFIA_CHOOSE: '🔴 *Mafiya, kim o\'lsin?*\n\nQurbon tanlang:',
  NIGHT_DOCTOR_CHOOSE: '💚 *Doktor, kimni davolaysiz?*\n\nSaqlamoqchi bo\'lgan o\'yinchini tanlang:',
  NIGHT_SHERIFF_CHOOSE: '🔵 *Sherif, kimni tekshirasiz?*\n\nTekshirmoqchi bo\'lgan o\'yinchini tanlang:',

  SHERIFF_MAFIA: (name) => `🔴 *${esc(name)}* — bu MAFIYA\\!`,
  SHERIFF_CLEAN: (name) => `✅ *${esc(name)}* — bu oddiy fuqaro\\.`,

  NIGHT_ACTION_RECORDED: '✅ Tanlovingiz qabul qilindi.',
  ALREADY_ACTED: "⚠️ Siz allaqachon harakat qildingiz.",

  DAY_KILLED: (round, name) =>
    `☀️ *KUN BOSHLANDI — ${round}\\-tur*\n\n😢 Kecha *${esc(name)}* o'ldirildi\\.\n\n60 soniya muhokama qiling, keyin ovoz berish boshlanadi\\.`,
  DAY_SAVED: (round) =>
    `☀️ *KUN BOSHLANDI — ${round}\\-tur*\n\n🍀 Kecha hech kim o'lmadi — doktor kimnidir saqlab qoldi\\!\n\n60 soniya muhokama qiling, keyin ovoz berish boshlanadi\\.`,

  VOTE_START: '🗳️ *OVOZ BERISH BOSHLANMOQDA\\!*\n\nKim o\'yindan chiqsin? Tanlang:',
  VOTE_SKIP: '⏭️ Hech kimni chiqarmaslik',
  VOTE_RECORDED: '✅ Ovozingiz qabul qilindi.',
  ALREADY_VOTED: "⚠️ Siz allaqachon ovoz berdingiz.",

  VOTE_ELIMINATED: (name, role) =>
    `🗳️ *Ovoz berish natijasi:*\n\n😵 *${esc(name)}* o'yindan chiqarildi\\! \\(Roli: ${esc(role)}\\)`,
  VOTE_TIE: '🗳️ *Ovoz berish natijasi:*\n\n🤝 Durang\\! Hech kim o\'yindan chiqarilmadi\\.',
  VOTE_SKIP_RESULT: '🗳️ *Ovoz berish natijasi:*\n\n⏭️ O\'yinchilar hech kimni chiqarmaslikni tanladi\\.',

  WIN_CITIZENS: (summary) =>
    `🎉 *FUQAROLAR YUTDI\\!*\n\nBarcha mafiya a'zolari topildi\\!\n\n*O'yinchilar:*\n${summary}`,
  WIN_MAFIA: (summary) =>
    `💀 *MAFIYA YUTDI\\!*\n\nMafiya fuqarolarni yengdi\\!\n\n*O'yinchilar:*\n${summary}`,

  PLAYER_DEAD: "☠️ Siz o'yindan chiqgansiz.",
  GAME_NOT_IN_NIGHT: "⚠️ Hozir tun fazasi emas.",
  GAME_NOT_IN_VOTE: "⚠️ Hozir ovoz berish fazasi emas.",
};

function esc(text) {
  return String(text).replace(/[_*[\]()~`>#+\-=|{}.!\\]/g, '\\$&');
}

module.exports.esc = esc;
