const ROLES = {
  MAFIA:   { key: 'mafia',   name: 'Mafiya', team: 'mafia', emoji: '🔴' },
  DOCTOR:  { key: 'doctor',  name: 'Doktor', team: 'town',  emoji: '💚' },
  SHERIFF: { key: 'sheriff', name: 'Sherif', team: 'town',  emoji: '🔵' },
  CITIZEN: { key: 'citizen', name: 'Fuqaro', team: 'town',  emoji: '⚪' },
};

function assignRoles(players) {
  const n = players.length;
  const mafiaCount = Math.max(1, Math.floor(n / 4));

  const roleList = [
    ...Array(mafiaCount).fill(ROLES.MAFIA),
    ROLES.DOCTOR,
    ROLES.SHERIFF,
    ...Array(n - mafiaCount - 2).fill(ROLES.CITIZEN),
  ];

  // Fisher-Yates shuffle
  for (let i = roleList.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [roleList[i], roleList[j]] = [roleList[j], roleList[i]];
  }

  players.forEach((p, i) => { p.role = roleList[i]; });
}

module.exports = { ROLES, assignRoles };
