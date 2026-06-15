const topics = [
  "present simple be: positive and negative",
  "present simple be: questions",
  "a/an and plural nouns; this, that, these, those",
  "possessive adjectives and apostrophes",
  "have/has got",
  "using adjectives",
  "present simple positive",
  "adverbs of frequency",
  "present simple negative",
  "present simple yes/no questions; short answers",
  "have to / don't have to",
  "question words",
  "there is / are",
  "can",
  "imperatives",
  "likes and dislikes",
  "was / were",
  "past simple regular and irregular verbs",
  "could",
  "past simple negative",
  "past simple questions",
  "countable and uncountable nouns; some and any",
  "much, many, a lot of",
  "a / an, the, no article",
  "present continuous",
  "present simple vs present continuous",
  "object pronouns",
  "comparatives",
  "superlatives",
  "verb + to + infinitive",
  "should and shouldn't",
  "present perfect",
  "present perfect vs past simple",
  "going to",
  "will for predictions",
  "might"
];

const questionTypes = [
  { id: "mixed", label: "Mixed question types" },
  { id: "multiple-choice", label: "Multiple choice" },
  { id: "gap-fill", label: "Gap fill" },
  { id: "rewrite", label: "Rewrite the sentence" },
  { id: "error-correction", label: "Find and correct the mistake" },
  { id: "make-question", label: "Make a question" },
  { id: "short-answer", label: "Short answer" },
  { id: "matching", label: "Matching" },
  { id: "paraphrase", label: "English paraphrase" }
];

const people = ["Tom", "Emma", "Mia", "Jack", "Sally", "Omar", "Lina", "Ben"];
const places = ["at school", "in London", "at the museum", "in the kitchen", "at work", "on the bus"];
const verbs = [
  { base: "play", third: "plays", past: "played", pp: "played", ing: "playing" },
  { base: "study", third: "studies", past: "studied", pp: "studied", ing: "studying" },
  { base: "watch", third: "watches", past: "watched", pp: "watched", ing: "watching" },
  { base: "go", third: "goes", past: "went", pp: "gone", ing: "going" },
  { base: "eat", third: "eats", past: "ate", pp: "eaten", ing: "eating" },
  { base: "write", third: "writes", past: "wrote", pp: "written", ing: "writing" },
  { base: "make", third: "makes", past: "made", pp: "made", ing: "making" },
  { base: "see", third: "sees", past: "saw", pp: "seen", ing: "seeing" },
  { base: "visit", third: "visits", past: "visited", pp: "visited", ing: "visiting" },
  { base: "read", third: "reads", past: "read", pp: "read", ing: "reading" }
];
const adjectives = ["interesting", "expensive", "beautiful", "easy", "cold", "friendly", "busy", "good", "bad", "big"];
const comparative = { interesting: "more interesting", expensive: "more expensive", beautiful: "more beautiful", easy: "easier", cold: "colder", friendly: "friendlier", busy: "busier", good: "better", bad: "worse", big: "bigger" };
const superlative = { interesting: "the most interesting", expensive: "the most expensive", beautiful: "the most beautiful", easy: "the easiest", cold: "the coldest", friendly: "the friendliest", busy: "the busiest", good: "the best", bad: "the worst", big: "the biggest" };

let lastQuestions = [];

const $ = (id) => document.getElementById(id);
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const shuffle = (arr) => [...arr].sort(() => Math.random() - 0.5);
const personIsThird = (name) => !["I", "you", "we", "they"].includes(name.toLowerCase());

function init() {
  $("topicSelect").innerHTML = `<option value="mixed">Mixed topics</option>` + topics.map((t) => `<option>${t}</option>`).join("");
  $("typeSelect").innerHTML = questionTypes.map((t) => `<option value="${t.id}">${t.label}</option>`).join("");
  $("topicChips").innerHTML = topics.map((topic, index) => `
    <label class="chip"><input type="checkbox" value="${topic}" ${index < 10 ? "checked" : ""}>${topic}</label>
  `).join("");

  $("generateBtn").addEventListener("click", generateWorksheet);
  $("checkBtn").addEventListener("click", checkAnswers);
  $("revealBtn").addEventListener("click", revealAnswers);
  $("printBtn").addEventListener("click", () => window.print());
  $("randomizeBtn").addEventListener("click", randomizeSettings);
  $("selectAllTopics").addEventListener("click", () => setTopicChecks(true));
  $("clearTopics").addEventListener("click", () => setTopicChecks(false));
  $("topicSelect").addEventListener("change", syncTopicFromSelect);

  generateWorksheet();
}

function setTopicChecks(value) {
  document.querySelectorAll("#topicChips input").forEach((input) => input.checked = value);
}

function syncTopicFromSelect() {
  const selected = $("topicSelect").value;
  if (selected === "mixed") return;
  document.querySelectorAll("#topicChips input").forEach((input) => input.checked = input.value === selected);
}

function randomizeSettings() {
  $("topicSelect").value = "mixed";
  $("typeSelect").value = pick(questionTypes).id;
  $("countInput").value = pick([8, 10, 12, 15, 20]);
  document.querySelectorAll("#topicChips input").forEach((input) => input.checked = Math.random() > 0.5);
  if (!selectedTopics().length) setTopicChecks(true);
  generateWorksheet();
}

function selectedTopics() {
  const dropdown = $("topicSelect").value;
  if (dropdown !== "mixed") return [dropdown];
  const chosen = [...document.querySelectorAll("#topicChips input:checked")].map((input) => input.value);
  return chosen.length ? chosen : topics;
}

function selectedTypes() {
  const type = $("typeSelect").value;
  if (type !== "mixed") return [type];
  return questionTypes.filter((item) => item.id !== "mixed").map((item) => item.id);
}

function generateWorksheet() {
  const count = Math.max(1, Math.min(40, Number($("countInput").value) || 12));
  const chosenTopics = shuffle(selectedTopics());
  const chosenTypes = shuffle(selectedTypes());
  lastQuestions = Array.from({ length: count }, () => {
    const topic = pick(chosenTopics);
    const type = pick(chosenTypes);
    return buildQuestion(topic, type);
  });
  $("scoreBox").textContent = "Not checked";
  render();
}

function render() {
  const container = $("questions");
  container.classList.remove("empty");
  container.innerHTML = lastQuestions.map((q, index) => questionHtml(q, index + 1)).join("");
  $("worksheetTitle").textContent = selectedTopics().length === 1 ? selectedTopics()[0] : "Mixed B1 grammar practice";
  $("questionCount").textContent = `${lastQuestions.length} questions`;
  $("topicCount").textContent = `${new Set(lastQuestions.map((q) => q.topic)).size} topics`;
}

function questionHtml(q, number) {
  return `
    <article class="question" data-index="${number - 1}">
      <div class="num">${number}</div>
      <div>
        <div class="q-type">${q.typeLabel} / ${q.topic}</div>
        <p class="prompt">${q.prompt}</p>
        ${answerControl(q, number - 1)}
        ${q.hint ? `<p class="hint">${q.hint}</p>` : ""}
        <p class="feedback" aria-live="polite"></p>
      </div>
    </article>
  `;
}

function answerControl(q, index) {
  if (q.kind === "choice") {
    return `<div class="options">${q.options.map((option, optionIndex) => `
      <label class="option">
        <input type="radio" name="answer-${index}" value="${escapeHtml(option)}">
        <span><strong>${String.fromCharCode(97 + optionIndex)})</strong> ${option}</span>
      </label>
    `).join("")}</div>`;
  }
  if (q.kind === "matching") {
    return `<input class="answer-input" data-answer-input="${index}" placeholder="Example: 1-b, 2-a, 3-d, 4-c" autocomplete="off">`;
  }
  return `<input class="answer-input" data-answer-input="${index}" placeholder="Type your answer" autocomplete="off">`;
}

function checkAnswers() {
  let correct = 0;
  lastQuestions.forEach((q, index) => {
    const article = document.querySelector(`.question[data-index="${index}"]`);
    const userAnswer = getUserAnswer(q, index);
    const isCorrect = isAnswerCorrect(userAnswer, q.accepted);
    article.classList.toggle("correct", isCorrect);
    article.classList.toggle("wrong", !isCorrect);
    article.querySelector(".feedback").textContent = isCorrect
      ? "Correct."
      : `Not quite. Correct answer: ${q.answer}`;
    if (isCorrect) correct += 1;
  });
  $("scoreBox").textContent = `${correct}/${lastQuestions.length} correct`;
}

function revealAnswers() {
  lastQuestions.forEach((q, index) => {
    const article = document.querySelector(`.question[data-index="${index}"]`);
    article.classList.remove("correct", "wrong");
    article.querySelector(".feedback").textContent = `Answer: ${q.answer}`;
  });
  $("scoreBox").textContent = "Answers revealed";
}

function getUserAnswer(q, index) {
  if (q.kind === "choice") {
    const checked = document.querySelector(`input[name="answer-${index}"]:checked`);
    return checked ? checked.value : "";
  }
  return document.querySelector(`[data-answer-input="${index}"]`)?.value || "";
}

function isAnswerCorrect(userAnswer, accepted) {
  const normalized = normalize(userAnswer);
  return accepted.some((answer) => normalize(answer) === normalized);
}

function normalize(text) {
  return String(text)
    .toLowerCase()
    .replace(/[.,!?]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function buildQuestion(topic, type) {
  const builders = {
    "multiple-choice": multipleChoice,
    "gap-fill": gapFill,
    "rewrite": rewrite,
    "error-correction": errorCorrection,
    "make-question": makeQuestion,
    "short-answer": shortAnswer,
    "matching": matching,
    "paraphrase": paraphrase
  };
  return builders[type](topic);
}

function baseQuestion(topic, typeId, prompt, answer, extras = {}) {
  return {
    topic,
    typeLabel: questionTypes.find((t) => t.id === typeId).label,
    prompt,
    answer,
    accepted: [answer],
    kind: "text",
    ...extras
  };
}

function multipleChoice(topic) {
  const data = answerForTopic(topic);
  return baseQuestion(topic, "multiple-choice", data.prompt, data.answer, {
    kind: "choice",
    accepted: [data.answer],
    options: shuffle([data.answer, ...data.distractors]).slice(0, 4)
  });
}

function gapFill(topic) {
  const data = answerForTopic(topic);
  const prompt = data.prompt.replace("___", '<span class="line"></span>');
  return baseQuestion(topic, "gap-fill", prompt, data.answer, {
    hint: "Complete the sentence with the correct B1 grammar form."
  });
}

function rewrite(topic) {
  const p = pick(people);
  const v = pick(verbs);
  const samples = {
    "present simple negative": [`${p} ${v.third} coffee before school.`, `${p} doesn't ${v.base} coffee before school.`],
    "past simple negative": [`${p} ${v.past} dinner at home last night.`, `${p} didn't ${v.base} dinner at home last night.`],
    "present continuous": [`${p} watches TV at the moment.`, `${p} is watching TV at the moment.`],
    "comparatives": ["This test is not as easy as the last one.", "The last test was easier than this one."],
    "superlatives": ["No student in the class is taller than Jack.", "Jack is the tallest student in the class."],
    "present perfect": [`${p} started living here in 2020.`, `${p} has lived here since 2020.`],
    "going to": [`${p} plans to visit Paris next summer.`, `${p} is going to visit Paris next summer.`],
    "should and shouldn't": ["It is a bad idea to eat so much sugar.", "You shouldn't eat so much sugar."]
  };
  const [source, answer] = samples[topic] || [`${p} can speak English well.`, `${p} is able to speak English well.`];
  return baseQuestion(topic, "rewrite", `Rewrite the sentence without changing the meaning:<br><strong>${source}</strong>`, answer);
}

function errorCorrection(topic) {
  const p = pick(people);
  const v = pick(verbs);
  const samples = {
    "present simple be: positive and negative": [`${p} are not from Spain.`, `${p} is not from Spain.`],
    "present simple be: questions": [`Are ${p} at home now?`, `Is ${p} at home now?`],
    "have/has got": [`${p} have got a new laptop.`, `${p} has got a new laptop.`],
    "present simple positive": [`${p} play football every weekend.`, `${p} plays football every weekend.`],
    "present simple yes/no questions; short answers": [`Does ${p} plays tennis?`, `Does ${p} play tennis?`],
    "past simple questions": [`Did ${p} went to school yesterday?`, `Did ${p} go to school yesterday?`],
    "present continuous": [`${p} is watch TV now.`, `${p} is watching TV now.`],
    "present perfect vs past simple": [`${p} has seen that film yesterday.`, `${p} saw that film yesterday.`],
    "should and shouldn't": ["You should to study tonight.", "You should study tonight."]
  };
  const [wrong, answer] = samples[topic] || [`${p} didn't ${v.past} the email.`, `${p} didn't ${v.base} the email.`];
  return baseQuestion(topic, "error-correction", `Find and correct the mistake:<br><strong>${wrong}</strong>`, answer);
}

function makeQuestion(topic) {
  const p = pick(people);
  const v = pick(verbs);
  const samples = {
    "question words": [`Where / ${p} / usually / study?`, `Where does ${p} usually study?`],
    "past simple questions": [`What / ${p} / buy / yesterday?`, `What did ${p} buy yesterday?`],
    "present simple be: questions": [`${p} / from / Turkey?`, `Is ${p} from Turkey?`],
    "present continuous": [`What / ${p} / do / now?`, `What is ${p} doing now?`],
    "going to": [`When / ${p} / visit / Ankara?`, `When is ${p} going to visit Ankara?`],
    "present perfect": [`How long / ${p} / know / Emma?`, `How long has ${p} known Emma?`]
  };
  const [prompt, answer] = samples[topic] || [`Who / ${v.base} / tennis / every weekend?`, "Who plays tennis every weekend?"];
  return baseQuestion(topic, "make-question", `Make a question with the prompts:<br><strong>${prompt}</strong>`, answer);
}

function shortAnswer(topic) {
  const p = pick(people);
  const v = pick(verbs);
  const samples = {
    "present simple be: questions": [`Is ${p} tired?`, `Yes, he is.`],
    "present simple yes/no questions; short answers": [`Does ${p} ${v.base} every day?`, `Yes, he does.`],
    "past simple questions": [`Did ${p} ${v.base} yesterday?`, `No, he didn't.`],
    "can": [`Can ${p} swim?`, `Yes, he can.`],
    "could": [`Could ${p} read when he was five?`, `No, he couldn't.`],
    "present perfect": [`Has ${p} ever ${v.pp} sushi?`, `Yes, he has.`],
    "will for predictions": ["Will it rain tomorrow?", "No, it won't."]
  };
  const [prompt, answer] = samples[topic] || [`Has ${p} got a bike?`, "Yes, he has."];
  return baseQuestion(topic, "short-answer", prompt, answer);
}

function matching(topic) {
  const left = ["1. Where do you live?", "2. How often do you study?", "3. Can you help me?", "4. What did she buy?"];
  const right = ["a) Every evening.", "b) In Izmir.", "c) A new jacket.", "d) Yes, of course."];
  return baseQuestion(topic, "matching", `Match the questions and answers:<div class="match-grid">${left.map((x) => `<div>${x}</div>`).join("")}${shuffle(right).map((x) => `<div>${x}</div>`).join("")}</div>`, "1-b, 2-a, 3-d, 4-c", {
    kind: "matching",
    accepted: ["1-b, 2-a, 3-d, 4-c", "1b 2a 3d 4c"]
  });
}

function paraphrase(topic) {
  const samples = {
    "there is / are": ["A room contains three students.", "There are three students in the room."],
    "can": ["I am able to play the piano.", "I can play the piano."],
    "have to / don't have to": ["It is necessary for me to get up early tomorrow.", "I have to get up early tomorrow."],
    "might": ["Perhaps it will rain this evening.", "It might rain this evening."],
    "should and shouldn't": ["It is a good idea for you to drink more water.", "You should drink more water."],
    "present continuous": ["I am in the middle of reading a book.", "I am reading a book now."],
    "present perfect": ["She has never visited London.", "She has never been to London."],
    "going to": ["I plan to study at the weekend.", "I am going to study at the weekend."]
  };
  const [source, answer] = samples[topic] || ["He studies English every day.", "He studies English every day."];
  return baseQuestion(topic, "paraphrase", `Write the sentence another way:<br><strong>${source}</strong>`, answer);
}

function answerForTopic(topic) {
  const p = pick(people);
  const place = pick(places);
  const v = pick(verbs);
  const adj = pick(adjectives);
  const isThird = personIsThird(p);
  const simpleVerb = isThird ? v.third : v.base;
  const data = {
    "present simple be: positive and negative": [`${p} ___ ${place} today.`, "is", ["are", "am", "be"]],
    "present simple be: questions": [`___ ${p} from Turkey?`, "Is", ["Are", "Am", "Be"]],
    "a/an and plural nouns; this, that, these, those": ["Look at ___ orange on the table.", "an", ["a", "these", "those"]],
    "possessive adjectives and apostrophes": ["This is Emma's bag. It is ___ bag.", "her", ["his", "their", "our"]],
    "have/has got": [`${p} ___ got two cousins.`, isThird ? "has" : "have", isThird ? ["have", "is", "does"] : ["has", "are", "do"]],
    "using adjectives": [`The film was very ___.`, adj, shuffle(adjectives.filter((a) => a !== adj)).slice(0, 3)],
    "present simple positive": [`${p} ___ English every day.`, simpleVerb, [v.base, v.ing, v.past]],
    "adverbs of frequency": ["Put the adverb in the correct place: I am late. (always)", "I am always late.", ["I always am late.", "Always I am late.", "I am late always."]],
    "present simple negative": [`${p} ___ like coffee.`, isThird ? "doesn't" : "don't", isThird ? ["don't", "isn't", "hasn't"] : ["doesn't", "isn't", "hasn't"]],
    "present simple yes/no questions; short answers": [`___ ${p} ${v.base} tennis?`, isThird ? "Does" : "Do", isThird ? ["Do", "Is", "Has"] : ["Does", "Are", "Have"]],
    "have to / don't have to": ["Students ___ wear a uniform at this school. It is a rule.", "have to", ["don't have to", "can", "might"]],
    "question words": ["___ do you live? In Ankara.", "Where", ["When", "Who", "How much"]],
    "there is / are": ["___ some apples in the bag.", "There are", ["There is", "It is", "They are"]],
    "can": ["Mia ___ speak Spanish very well.", "can", ["cans", "is can", "does can"]],
    "imperatives": ["___ your books, please.", "Open", ["Opens", "Opening", "To open"]],
    "likes and dislikes": ["I can't stand ___ early.", "getting up", ["get up", "to getting up", "got up"]],
    "was / were": ["They ___ at home last night.", "were", ["was", "are", "is"]],
    "past simple regular and irregular verbs": [`We ___ to the cinema yesterday.`, v.past, [v.base, v.third, v.ing]],
    "could": ["When I was six, I ___ ride a bike.", "could", ["can", "am able", "could to"]],
    "past simple negative": ["She ___ go to school yesterday.", "didn't", ["doesn't", "wasn't", "hasn't"]],
    "past simple questions": ["___ you see Tom last week?", "Did", ["Do", "Have", "Were"]],
    "countable and uncountable nouns; some and any": ["There isn't ___ milk in the fridge.", "any", ["some", "many", "a"]],
    "much, many, a lot of": ["How ___ money have you got?", "much", ["many", "a lot of", "some"]],
    "a / an, the, no article": ["I saw ___ Eiffel Tower in Paris.", "the", ["a", "an", "no article"]],
    "present continuous": [`${p} ___ ${v.ing} now.`, "is", ["are", "do", "has"]],
    "present simple vs present continuous": ["She usually walks, but today she ___ the bus.", "is taking", ["takes", "take", "took"]],
    "object pronouns": ["I like Tom. I like ___.", "him", ["he", "his", "her"]],
    "comparatives": [`This phone is ___ than that phone.`, comparative[adj], [adj, superlative[adj], "most " + adj]],
    "superlatives": [`This is ___ film in the class.`, superlative[adj], [comparative[adj], adj, "more " + adj]],
    "verb + to + infinitive": ["I want ___ a doctor.", "to be", ["being", "be", "to being"]],
    "should and shouldn't": ["You look tired. You ___ go to bed early.", "should", ["shouldn't", "mustn't", "don't have to"]],
    "present perfect": [`She has ___ her homework.`, v.pp, [v.past === v.pp ? v.base : v.past, v.ing, v.third]],
    "present perfect vs past simple": ["I ___ my homework yesterday.", "did", ["have done", "has done", "do"]],
    "going to": ["Look at those clouds. It ___ rain.", "is going to", ["will to", "going", "is go to"]],
    "will for predictions": ["I think people ___ live on Mars one day.", "will", ["are going", "can to", "will to"]],
    "might": ["Take an umbrella. It ___ rain later.", "might", ["must", "does", "is"]]
  };
  const [prompt, answer, distractors] = data[topic];
  return { prompt, answer, distractors };
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[char]));
}

init();
