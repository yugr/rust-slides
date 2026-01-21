awk '/^Internal stats: [0-9]+ [0-9]+$/{statics += $3; externs += $4} END{print statics " " externs " " (100 * statics / (statics + externs))}'
