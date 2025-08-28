
USE tournament;
GO

-- Step 2: Tournament Table
CREATE TABLE Tournament (
	T_ID INT PRIMARY KEY,
    Years INT,
    Host_country VARCHAR(100) NOT NULL,
    Formats VARCHAR(50) NOT NULL
);
GO

-- Step 3: Tournament_Groups Table
CREATE TABLE Tournament_Groups (
    G_ID INT PRIMARY KEY IDENTITY(1,1),
    GroupName VARCHAR(10) NOT NULL,
    T_ID INT NOT NULL,
    FOREIGN KEY (T_ID) REFERENCES Tournament(T_ID)
);
GO

-- Step 4: Teams Table
CREATE TABLE Teams (
    Team_ID INT PRIMARY KEY IDENTITY(1,1),
    TeamName VARCHAR(100) NOT NULL,
    G_ID INT,
    Abbreviation VARCHAR(5),
    FOREIGN KEY (G_ID) REFERENCES Tournament_Groups(G_ID)
);
GO

-- Step 5: Players Table
CREATE TABLE Player (
    Player_ID INT PRIMARY KEY IDENTITY(1,1),
    Team_ID INT NOT NULL,
    Name VARCHAR(100) NOT NULL,
    KitNumber INT,
    Role VARCHAR(50),
    FOREIGN KEY (Team_ID) REFERENCES Teams(Team_ID)
);
GO

-- Step 6: Venues Table
CREATE TABLE Venues (
    VenueID INT PRIMARY KEY IDENTITY(1,1),
    VenueName VARCHAR(250) NOT NULL,
    City VARCHAR(250),
    Country VARCHAR(250)
);
GO

-- Step 7: Matches Table
CREATE TABLE Matches (
    MatchID INT PRIMARY KEY IDENTITY(1,1),
    T_ID INT NOT NULL,
    Team1_ID INT NOT NULL,
    Team2_ID INT NOT NULL,
    Date DATETIME NOT NULL,
    VenueID INT,
    WinnerID INT,
    Stage VARCHAR(20) CHECK (Stage IN ('Group', 'Quarterfinal', 'Semifinal', 'Final')),
    FOREIGN KEY (T_ID) REFERENCES Tournament(T_ID),
    FOREIGN KEY (Team1_ID) REFERENCES Teams(Team_ID),
    FOREIGN KEY (Team2_ID) REFERENCES Teams(Team_ID),
    FOREIGN KEY (WinnerID) REFERENCES Teams(Team_ID),
    FOREIGN KEY (VenueID) REFERENCES Venues(VenueID)
);
GO

-- Step 8: MatchDetails Table
CREATE TABLE MatchDetails (
    Match_ID INT PRIMARY KEY,
    TossWinner INT NOT NULL,
    TossDecision VARCHAR(10) CHECK (TossDecision IN ('Bat', 'Bowl')),
    FirstInningsScore VARCHAR(20),
    SecondInningsScore VARCHAR(20),
    Result VARCHAR(100),
    PlayerOfMatch INT,
    FOREIGN KEY (Match_ID) REFERENCES Matches(MatchID),
    FOREIGN KEY (TossWinner) REFERENCES Teams(Team_ID),
    FOREIGN KEY (PlayerOfMatch) REFERENCES Player(Player_ID)
);
GO

-- Step 9: TeamPerformance Table
CREATE TABLE TeamPerformance (
    TeamPerf_ID INT PRIMARY KEY IDENTITY(1,1),
    Team_ID INT NOT NULL,
    Match_ID INT NOT NULL,
    RunsScored INT NOT NULL,
    WicketsLost INT NOT NULL,
    Fours INT DEFAULT 0,
    Sixes INT DEFAULT 0,
    Extras INT DEFAULT 0,
    FOREIGN KEY (Team_ID) REFERENCES Teams(Team_ID),
    FOREIGN KEY (Match_ID) REFERENCES Matches(MatchID),
    UNIQUE (Team_ID, Match_ID)
);
GO

-- Step 10: PlayerPerformance Table
CREATE TABLE PlayerPerformance (
    Perf_ID INT PRIMARY KEY IDENTITY(1,1),
    Player_ID INT NOT NULL,
    Match_ID INT NOT NULL,
    RunsScored INT DEFAULT 0,
    BallsFaced INT DEFAULT 0,
    Fours INT DEFAULT 0,
    Sixes INT DEFAULT 0,
    WicketsTaken INT DEFAULT 0,
    RunsConceded INT DEFAULT 0,
    OversBowled DECIMAL(3,1) DEFAULT 0,
    Catches INT DEFAULT 0,
    FOREIGN KEY (Player_ID) REFERENCES Player(Player_ID),
    FOREIGN KEY (Match_ID) REFERENCES Matches(MatchID),
    UNIQUE (Player_ID, Match_ID)
);
GO

-- Step 11: Standings Table
CREATE TABLE Standings (
    Standing_ID INT PRIMARY KEY IDENTITY(1,1),
    T_ID INT NOT NULL,
    Team_ID INT NOT NULL,
    MatchesPlayed INT DEFAULT 0,
    Wins INT DEFAULT 0,
    Losses INT DEFAULT 0,
    Points INT DEFAULT 0,
    NRR FLOAT DEFAULT 0,
    FOREIGN KEY (T_ID) REFERENCES Tournament(T_ID),
    FOREIGN KEY (Team_ID) REFERENCES Teams(Team_ID),
    UNIQUE (T_ID, Team_ID)
);
GO

select * from Matches;