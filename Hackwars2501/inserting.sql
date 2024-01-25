------------------- inserting into users -----------------------------
--Palps
INSERT INTO Users (name, alias, summary) VALUES
("Emperor Palpatine", "Sheev Palpatine | Dark Lord | Order 66 Ruler | Emperor | The Senate", "As Emperor Palpatine, I am the mastermind behind the Galactic Empire's rise and the embodiment of strength and control in the galaxy. From my humble beginnings as a Naboo Senator, I ascended to Supreme Chancellor, reshaping the Republic into a beacon of peace and order. My mantra, 'I am the Senate,' echoes my unlimited power. Join me in the journey towards a better, more orderly galaxy!");

-- Darth Vader
INSERT INTO Users (name, alias, summary) VALUES
("Darth Vader", "Anakin Skywalker | Dark Lord of the Sith | Right Hand of the Emperor | Proud Father", "As Darth Vader, I am the enforcer of Emperor Palpatine's will and a symbol of fear and power throughout the galaxy. Formerly Anakin Skywalker, I embraced the Dark Side to become the Sith Lord I am today. My unwavering loyalty to the Emperor and my signature phrase, 'I find your lack of faith disturbing,' emphasize my dedication to maintaining order and control. Also I don't like sand");

-- Grand Moff Tarkin
INSERT INTO Users (name, alias, summary) VALUES
("Grand Moff Tarkin", "Imperial Strategist | Death Star Commander", "As Grand Moff Tarkin, I am the architect of the Death Star, a symbol of the Empire's might. My unwavering loyalty to Emperor Palpatine and my strategic brilliance have earned me a reputation as a visionary leader. I firmly believe in the doctrine of fear and control to maintain order in the galaxy.");

-- Admiral Thrawn
INSERT INTO Users (name, alias, summary) VALUES
("Admiral Thrawn", "Chiss Strategist | Grand Admiral", "I am Admiral Thrawn, a Chiss strategist known for my unparalleled tactical brilliance. Serving as a Grand Admiral in the Imperial Navy, I bring a unique perspective to the Empire's military campaigns. My analytical mind and deep understanding of art and culture provide a fresh approach to warfare.");

-- Colonel Yularen
INSERT INTO Users (name, alias, summary) VALUES
("Colonel Yularen", "Imperial Intelligence | ISB Officer", "Colonel Wullf Yularen reporting. As an officer of the Imperial Security Bureau (ISB), I am dedicated to maintaining security and order within the Empire. With a background in military and intelligence, I ensure loyalty and compliance among Imperial personnel. My commitment to the Empire is unwavering.");




---------------- inserting into Jobdescriptions ------------------------
-- Emperor Palpatine's Job Descriptions
INSERT INTO JobDescriptions (user_id, title, description) VALUES
(1, "Senator in the Senate of the Grand Republic", "Expert political maneuvering led to my ascent from Naboo Senator to Supreme Chancellor. Adept in the art of persuasion and political strategy, securing unanimous support for crucial decisions. Masterminded the transformation of the Republic into the mighty Galactic Empire, ensuring lasting stability.");

INSERT INTO JobDescriptions (user_id, title, description) VALUES
(1, "Supreme Chancellor of the Galactic Republic | The Senate | CEO", "Orchestrated events during the Clone Wars, consolidating power under the guise of emergency measures. Implemented strategic policies, contributing to the downfall of the Jedi Order and the rise of the Empire. Championed the execution of Order 66, marking a turning point in galactic history.");

INSERT INTO JobDescriptions (user_id, title, description) VALUES
(1, "Emperor of the Galactic Empire | Founder", "Founded the Galactic Empire, ending the era of the Galactic Republic. Executed Order 66, effectively neutralizing the Jedi Order and cementing imperial control. Oversaw massive infrastructure projects, including the iconic Death Stars.");

INSERT INTO JobDescriptions (user_id, title, description) VALUES
(1, "Sith Master", "Mastered the Dark Side of the Force, possessing unrivaled power and knowledge. Mentored several apprentices, advancing the Sith legacy and ideology. Engineered the Jedi Order's fall, reshaping galactic history according to Sith principles. Utilized strategic foresight and manipulation to realize the Sith agenda.");

-- Darth Vader's Job Descriptions
INSERT INTO JobDescriptions (user_id, title, description) VALUES
(2, "Dark Lord of the Sith", "Embraced the Dark Side of the Force, harnessing its formidable power. Served as the Emperor's most trusted enforcer, carrying out critical missions and eliminating threats. Commanded the Imperial military, overseeing the Imperial Navy and Stormtrooper Corps.");

INSERT INTO JobDescriptions (user_id, title, description) VALUES
(2, "Jedi Knight (Formerly) | Chosen One (Formerly)", "Rose through the ranks of the Jedi Order, displaying exceptional combat skills and Force sensitivity. Fought valiantly during the Clone Wars, but ultimately succumbed to the lure of the Dark Side. Transformed into Darth Vader, embracing a new identity and becoming a pivotal figure in the Empire's hierarchy.");

INSERT INTO JobDescriptions (user_id, title, description) VALUES
(2, "Galactic Hero (Formerly)", "Distinguished career as a Jedi Knight, participating in many battles during the Clone Wars. Notable accomplishments include the rescue of Chancellor Palpatine from General Grievous and the defeat of countless Separatist forces.");

-- Grand Moff Tarkin's Job Descriptions
INSERT INTO JobDescriptions (user_id, title, description) VALUES
(3, "Grand Moff of the Outer Rim Territories", "Governed the Outer Rim Territories, extending the Empire's reach and influence. Masterminded the construction and deployment of the Death Star, a superweapon of unrivaled power. Advocated the use of the Death Star to quell rebellion and maintain order.");

INSERT INTO JobDescriptions (user_id, title, description) VALUES
(3, "Death Star Commander", "Oversaw the operation of the Death Star, ensuring its readiness and effectiveness. Authorized the destruction of Alderaan as a demonstration of Imperial power. Acted as a key figure in the Empire's strategy against the Rebel Alliance.");

-- Admiral Thrawn's Job Descriptions
INSERT INTO JobDescriptions (user_id, title, description) VALUES
(4, "Grand Admiral of the Imperial Navy", "Commanded the Imperial fleet, applying innovative tactics to outmaneuver Rebel forces. Analyzed the art and culture of opponents to gain insights into their strategies. Utilized my tactical genius to secure victories and expand Imperial influence.");

INSERT INTO JobDescriptions (user_id, title, description) VALUES
(4, "Chiss Commander (Formerly)", "Hailing from the Chiss Ascendancy, I gained recognition for my strategic prowess. Brought my expertise to the Empire, adapting Chiss tactics to Imperial campaigns. Earned the respect and fear of Rebel forces through my strategic victories.");

-- Colonel Yularen's Job Descriptions
INSERT INTO JobDescriptions (user_id, title, description) VALUES
(5, "ISB Officer (Colonel)", "Led ISB operations to identify and eliminate threats to the Empire from within. Ensured loyalty and adherence to Imperial doctrine among officers and personnel. Conducted intelligence gathering and counterinsurgency operations.");

INSERT INTO JobDescriptions (user_id, title, description) VALUES
(5, "Republic Admiral (Formerly)", "Served as a Republic Admiral during the Clone Wars, contributing to naval victories. Transitioned to the Imperial Navy, maintaining a position of authority and influence. Played a key role in transitioning the Republic into the Galactic Empire.");



---------Inserting Skills-----------------------
-- Skills for Emperor Palpatine
INSERT INTO Skills (user_id, skill) VALUES
(1, "Political Strategy"),
(1, "Persuasion"),
(1, "Leadership"),
(1, "Dark Side of the Force Mastery");

-- Skills for Darth Vader
INSERT INTO Skills (user_id, skill) VALUES
(2, "Lightsaber Combat"),
(2, "Force Sensitivity"),
(2, "Military Strategy"),
(2, "Intimidation Tactics");

-- Skills for Grand Moff Tarkin
INSERT INTO Skills (user_id, skill) VALUES
(3, "Strategic Planning"),
(3, "Leadership in Crisis"),
(3, "Territorial Administration"),
(3, "Commitment to Imperial Doctrine");

-- Skills for Admiral Thrawn
INSERT INTO Skills (user_id, skill) VALUES
(4, "Tactical Analysis"),
(4, "Art and Culture Assessment"),
(4, "Starship Warfare Mastery"),
(4, "Leadership and Adaptability");

-- Skills for Colonel Yularen
INSERT INTO Skills (user_id, skill) VALUES
(5, "Intelligence Analysis"),
(5, "Security Enforcement"),
(5, "Interrogation Techniques"),
(5, "Strategic Planning");
