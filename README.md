So, someone at work asked me about turning nfl pick-em into a linear optimization problem. After all, it really is an issue of clever resource allocation. I think the question was ultimately brought on by the following article: https://www.klittlepage.com/2013/08/12/hacking-an-nfl-survivor-pool-for-fun-and-profit/, where the author does something kind of similar. 

My biggest issue with his methology (and he aknowledges this too) is that he's maximizing (in theory) the total number of games you'd pick right ouf of the regular season, when he should've been maximizing the expected number of weeks you'd be alive in your survivor pool. In reality, you'd probably like to pick the more lopsided games earlier, to maximize your changes of still being in the game later in the season. 

So, I tried to maximize the expected number of weeks you'd last, using the probability predictions from http://projects.fivethirtyeight.com/2016-nfl-predictions/. The first part of this code is just a way of compiling some copy/pastes from that website, since it's awfully hard to find free nfl probability predictions for some reason. 

So since my work pays like 100k for its Gurobi license, and I get the impression I can use it on the weekends, and considering that this problem took it like 3 seconds, I decided to go for it. Note that I'm maximizing logs of products and stuff, which is a bit of a hack, but I think it's alright for something that I'm going to spend only a little bit of time writing while waiting for the cowboy/packer game to start. 

The results? 

KC_week_1
DET_week_2
SEA_week_3
HOU_week_4
CAR_week_5
PIT_week_6
CIN_week_7
DEN_week_8
MIN_week_9
ARI_week_10
BUF_week_12
BAL_week_13
NE_week_14
ATL_week_15
PHI_week_16
IND_week_17

Which would've had me out by the second week. I blame fivethirtyeight for giving the lions an 80% chance of winning that game at home. 
