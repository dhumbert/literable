TRUNCATE TABLE authors CASCADE;
TRUNCATE TABLE books CASCADE;
TRUNCATE TABLE genres CASCADE;
TRUNCATE TABLE series CASCADE;
TRUNCATE TABLE tags CASCADE;

--
-- Data for Name: authors; Type: TABLE DATA; Schema: public; Owner: goread
--

INSERT INTO authors (id, name, slug) VALUES (12, 'D.H. Lawrence', 'd-h-lawrence');
INSERT INTO authors (id, name, slug) VALUES (13, 'F. Scott Fitzgerald', 'f-scott-fitzgerald');
INSERT INTO authors (id, name, slug) VALUES (14, 'Jack London', 'jack-london');
INSERT INTO authors (id, name, slug) VALUES (15, 'Nikolai Gogol', 'nikolai-gogol');
INSERT INTO authors (id, name, slug) VALUES (16, 'Robert Louis Stevenson', 'robert-louis-stevenson');
INSERT INTO authors (id, name, slug) VALUES (17, 'Rudyard Kipling', 'rudyard-kipling');
INSERT INTO authors (id, name, slug) VALUES (18, 'Alexandre Dumas', 'alexandre-dumas');
INSERT INTO authors (id, name, slug) VALUES (19, 'Charles Stross', 'charles-stross');
INSERT INTO authors (id, name, slug) VALUES (20, 'Sir Arthur Conan Doyle', 'sir-arthur-conan-doyle');
INSERT INTO authors (id, name, slug) VALUES (21, 'Andrew Lang', 'andrew-lang');
INSERT INTO authors (id, name, slug) VALUES (22, 'Henry Kuttner', 'henry-kuttner');


--
-- Name: authors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: goread
--

SELECT pg_catalog.setval('authors_id_seq', 22, true);


--
-- Data for Name: genres; Type: TABLE DATA; Schema: public; Owner: goread
--

INSERT INTO genres (id, name, slug, parent_id) VALUES (15, 'Fiction', 'fiction', NULL);
INSERT INTO genres (id, name, slug, parent_id) VALUES (16, 'Science Fiction', 'science-fiction', 15);
INSERT INTO genres (id, name, slug, parent_id) VALUES (17, 'Historical Fiction', 'historical-fiction', 15);
INSERT INTO genres (id, name, slug, parent_id) VALUES (18, 'Fantasy', 'fantasy', 15);
INSERT INTO genres (id, name, slug, parent_id) VALUES (19, 'Mystery', 'mystery', 15);


--
-- Data for Name: series; Type: TABLE DATA; Schema: public; Owner: goread
--

INSERT INTO series (id, title, slug, description) VALUES (4, 'Example Series', 'example-series', NULL);


--
-- Data for Name: books; Type: TABLE DATA; Schema: public; Owner: goread
--

INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (23, 'The Sea Wolf', 'Jack_London_-_The_Sea_Wolf.epub', 'seawolf.jpg', 'Humphrey Van Weyden becomes an unwilling participant in a tense shipboard drama. A deranged and abusive sea captain perpetrates a shipboard atmosphere of increasing violence that ultimately boils into mutiny, shipwreck, and a desperate confrontation. This 1904 maritime classic depicts the clash of materialistic and idealistic cultures with a mixture of gritty realism and sublime lyricism.', 15, NULL, NULL, 14, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (25, 'Kidnapped', 'Robert_Louis_Stevenson_-_Kidnapped.epub', 'kidnapped.jpg', 'The young orphan David Balfour is sent to live with his Uncle Ebenezer. When he discovers that he may be the rightful heir to his uncle s estate, he finds himself kidnapped and cast away on a desert isle. A historical adventure novel originally intended for a young-adult audience, Kidnapped deals with true historical events relating to the Jacobite Rising, and has won the admiration of an adult audience.', 15, NULL, NULL, 16, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (19, 'The White Company', 'Arthur_Conan_Doyle_-_The_White_Company.epub', 'whitecompany.jpg', '"The White Company" by Arthur Conan Doyle was the best selling book of its time. Set in the mediaeval era, this work presents a time when swordsmen and archers were the best kind of army. From Britain to France and Spain, the book takes you on an unforgettable journey that is brimming with adventure and excitement!', 17, NULL, NULL, 20, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (26, 'Just So Stories', 'Rudyard_Kipling_-_Just_so_Stories.epub', 'justsostories.jpg', 'A dozen fables by one of the world''s great storytellers propose whimsical explanations of how certain animals acquired their distinctive physical characteristics: "How the Camel Got His Hump," "How the Whale Got His Throat," "How the Leopard Got His Spots," "How the Rhinoceros Got His Skin," "The Elephant''s Child," and 7 others. ', 15, 4, 2, 17, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (18, 'The Man in the Iron Mask', 'Alexandre_Dumas_-_The_Man_in_the_Iron_Mask.epub', 'mainironmask.jpg', 'Alexandre Dumas was already a best-selling novelist when he wrote this historical romance, combining (as he claimed) the two essentials of life--"l''action et l''amour." The Man in the Iron Mask concludes the epic adventures of the three Muskateers, as Athos, Porthos, Aramis, and their friend D''Artagnan, once invincible, meet their destinies.', 15, NULL, NULL, 18, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (24, 'Dead Souls', 'Nikolai_Gogol_-_Dead_Souls.epub', 'deadsouls.jpg', 'Since its publication in 1842, Dead Souls has been celebrated as a supremely realistic portrait of provincial Russian life and as a splendidly exaggerated tale; as a paean to the Russian spirit and as a remorseless satire of imperial Russian venality, vulgarity, and pomp. As Gogol''s wily antihero, Chichikov, combs the back country wheeling and dealing for "dead souls"--deceased serfs who still represent money to anyone sharp enough to trade in them--we are introduced to a Dickensian cast of peasants, landowners, and conniving petty officials, few of whom can resist the seductive illogic of Chichikov''s proposition.', 15, NULL, NULL, 15, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (21, 'Sons and Lovers', 'David_Herbert_Lawrence_-_Sons_and_Lovers.epub', 'sonsandlovers.jpg', 'This semi-autobiographical novel explores the emotional conflicts through the protagonist, Paul Morel, and the suffocating relationships with a demanding mother and two very different lovers. It is a pre-Freudian exploration of love and possessiveness.', 15, NULL, NULL, 12, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (22, 'Tender is the Night', 'Francis_Scott_Fitzgerald_-_Tender_is_the_Night.epub', 'tenderisnight.jpg', 'Published in 1934, Tender Is the Night was one of the most talked-about books of the year. "It''s amazing how excellent much of it is," Ernest Hemingway said to Maxwell Perkins. "I will say now," John O''Hara wrote Fitzgerald, "Tender Is the Night is in the early stages of being my favorite book, even more than This Side of Paradise." And Archibald MacLeish exclaimed: "Great God, Scott...You are a fine writer. Believe it -- not me." 

Set on the French Riviera in the late 1920s, Tender Is the Night is the tragic romance of the young actress Rosemary Hoyt and the stylish American couple Dick and Nicole Diver. A brilliant young psychiatrist at the time of his marriage, Dick is both husband and doctor to Nicole, whose wealth goads him into a lifestyle not his own, and whose growing strength highlights Dick''s harrowing demise. A profound study of the romantic concept of character -- lyrical, expansive, and hauntingly evocative -- Tender Is the Night, Mabel Dodge Luhan remarked, raised F. Scott Fitzgerald to the heights of "a modern Orpheus."', 15, NULL, NULL, 13, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (20, 'Accelerando', 'Charles_Stross_-_Accelerando.epub', 'Accelerando_book_cover.jpg', 'The Singularity. It is the era of the posthuman. Artificial intelligences have surpassed the limits of human intellect. Biotechnological beings have rendered people all but extinct. Molecular nanotechnology runs rampant, replicating and reprogramming at will. Contact with extraterrestrial life grows more imminent with each new day.

Struggling to survive and thrive in this accelerated world are three generations of the Macx clan: Manfred, an entrepreneur dealing in intelligence amplification technology whose mind is divided between his physical environment and the Internet; his daughter, Amber, on the run from her domineering mother, seeking her fortune in the outer system as an indentured astronaut; and Sirhan, Amber’s son, who finds his destiny linked to the fate of all of humanity.

For something is systematically dismantling the nine planets of the solar system. Something beyond human comprehension. Something that has no use for biological life in any form...', 16, 4, 1, 19, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (27, 'The Red Fairy Book', 'Andrew_Lang_-_The_Red_Fairy_Book.epub', 'red-fairy.jpeg', 'The famed folklorist collects 37 tales of enchantment, ranging from the familiar ("Rapunzel," "Jack and the Beanstalk," and "The Golden Goose") to lesser-known stories ("The Voice of Death," "The Enchanted Pig," and "The Master Thief"). Sources include French, Russian, Danish, and Romanian tales as well as Norse mythology.', 18, NULL, NULL, 21, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (28, 'The Return of Sherlock Holmes', 'Arthur_Conan_Doyle_-_The_Return_of_Sherlock_Holmes.epub', 'return-of-sherlock-holmes.jpg', 'The Return of Sherlock Holmes by Sir Arthur Conan Doyle, is a collection of 13 Sherlock Holmes stories, originally published in 1903-1904

This was the first Holmes collection since 1893, when Holmes had, "apparently", died, in "The Adventure of the Final Problem". 

Having published The Hound of the Baskervilles in 1901 - 1902, although setting it before Holmes'' death, Doyle came under intense pressure to revive his famous character, which he did in "The Adventure of the Empty House", in this collection.

Stories included in The Return of Sherlock Holmes:

"The Adventure of the Empty House"
"The Adventure of the Norwood Builder"
"The Adventure of the Dancing Men"
"The Adventure of the Solitary Cyclist"
"The Adventure of the Priory School"
"The Adventure of Black Peter"
"The Adventure of Charles Augustus Milverton"
"The Adventure of the Six Napoleons"
"The Adventure of the Three Students"
"The Adventure of the Golden Pince-Nez"
"The Adventure of the Missing Three-Quarter"
"The Adventure of the Abbey Grange"
"The Adventure of the Second Stain"', 19, NULL, NULL, 20, NULL, NULL);
INSERT INTO books (id, title, filename, cover, description, genre_id, series_id, series_seq, author_id, created_at, rating) VALUES (29, 'The Dark World', 'Henry_Kuttner_-_The_Dark_World.epub', 'darkworld.jpeg', 'Henry Kuttner''s Sword and Sorcery classic returns to print at last! World War II veteran Edward Bond''s recuperation from a disastrous fighter plane crash takes a distinct turn for the weird when he encounters a giant wolf, a red witch, and the undeniable power of the need-fire, a portal to a world of magic and swordplay at once terribly new and hauntingly familiar. In the Dark World, Bond opposes the machinations of the dread lord Ganelon and his terrible retinue of werewolves, wizards, and witches, but all is not as it seems in this shadowy mirror of the real world, and Bond discovers that a part of him feels more at home here than he ever has on Earth.', 18, NULL, NULL, 22, NULL, NULL);


--
-- Name: books_id_seq; Type: SEQUENCE SET; Schema: public; Owner: goread
--

SELECT pg_catalog.setval('books_id_seq', 29, true);


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: goread
--

INSERT INTO tags (id, name, slug) VALUES (8, 'russia', 'russia');
INSERT INTO tags (id, name, slug) VALUES (9, 'peasants', 'peasants');
INSERT INTO tags (id, name, slug) VALUES (10, 'animals', 'animals');
INSERT INTO tags (id, name, slug) VALUES (11, 'short stories', 'short-stories');
INSERT INTO tags (id, name, slug) VALUES (12, 'pirates', 'pirates');
INSERT INTO tags (id, name, slug) VALUES (13, 'britain', 'britain');
INSERT INTO tags (id, name, slug) VALUES (14, 'romance', 'romance');
INSERT INTO tags (id, name, slug) VALUES (15, 'france', 'france');
INSERT INTO tags (id, name, slug) VALUES (16, '1920s', '1920s');
INSERT INTO tags (id, name, slug) VALUES (17, 'sailing', 'sailing');
INSERT INTO tags (id, name, slug) VALUES (18, 'mutiny', 'mutiny');
INSERT INTO tags (id, name, slug) VALUES (19, 'musketeers', 'musketeers');
INSERT INTO tags (id, name, slug) VALUES (20, 'singularity', 'singularity');
INSERT INTO tags (id, name, slug) VALUES (21, 'biotechnology', 'biotechnology');
INSERT INTO tags (id, name, slug) VALUES (22, 'medieval', 'medieval');
INSERT INTO tags (id, name, slug) VALUES (23, 'mythology', 'mythology');
INSERT INTO tags (id, name, slug) VALUES (24, 'detective', 'detective');
INSERT INTO tags (id, name, slug) VALUES (25, 'witches', 'witches');
INSERT INTO tags (id, name, slug) VALUES (26, 'wizards', 'wizards');


--
-- Data for Name: books_tags; Type: TABLE DATA; Schema: public; Owner: goread
--

INSERT INTO books_tags (tag_id, book_id) VALUES (11, 27);
INSERT INTO books_tags (tag_id, book_id) VALUES (23, 27);
INSERT INTO books_tags (tag_id, book_id) VALUES (11, 28);
INSERT INTO books_tags (tag_id, book_id) VALUES (24, 28);
INSERT INTO books_tags (tag_id, book_id) VALUES (25, 29);
INSERT INTO books_tags (tag_id, book_id) VALUES (26, 29);
INSERT INTO books_tags (tag_id, book_id) VALUES (8, 24);
INSERT INTO books_tags (tag_id, book_id) VALUES (9, 24);
INSERT INTO books_tags (tag_id, book_id) VALUES (14, 21);
INSERT INTO books_tags (tag_id, book_id) VALUES (15, 22);
INSERT INTO books_tags (tag_id, book_id) VALUES (16, 22);
INSERT INTO books_tags (tag_id, book_id) VALUES (17, 23);
INSERT INTO books_tags (tag_id, book_id) VALUES (18, 23);
INSERT INTO books_tags (tag_id, book_id) VALUES (13, 25);
INSERT INTO books_tags (tag_id, book_id) VALUES (12, 25);
INSERT INTO books_tags (tag_id, book_id) VALUES (17, 25);
INSERT INTO books_tags (tag_id, book_id) VALUES (15, 18);
INSERT INTO books_tags (tag_id, book_id) VALUES (19, 18);
INSERT INTO books_tags (tag_id, book_id) VALUES (14, 18);
INSERT INTO books_tags (tag_id, book_id) VALUES (22, 19);
INSERT INTO books_tags (tag_id, book_id) VALUES (13, 19);
INSERT INTO books_tags (tag_id, book_id) VALUES (15, 19);
INSERT INTO books_tags (tag_id, book_id) VALUES (21, 20);
INSERT INTO books_tags (tag_id, book_id) VALUES (20, 20);
INSERT INTO books_tags (tag_id, book_id) VALUES (10, 26);
INSERT INTO books_tags (tag_id, book_id) VALUES (11, 26);


--
-- Name: genres_id_seq; Type: SEQUENCE SET; Schema: public; Owner: goread
--

SELECT pg_catalog.setval('genres_id_seq', 19, true);


--
-- Name: series_id_seq; Type: SEQUENCE SET; Schema: public; Owner: goread
--

SELECT pg_catalog.setval('series_id_seq', 4, true);


--
-- Name: tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: goread
--

SELECT pg_catalog.setval('tags_id_seq', 26, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: goread
--

INSERT INTO users (id, username, password) VALUES (3, 'demo', '89e495e7941cf9e40e6980d14a16bf023ccd4c91');


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: goread
--

SELECT pg_catalog.setval('users_id_seq', 3, true);


--
-- PostgreSQL database dump complete
--

