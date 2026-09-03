---
title: The Dog or the Pig
date: 2026-11-08
tldr: Humans keep dogs on the couch and pigs in factories. If AI becomes the stronger species, which one are we, and can we measure it?
status: published
---

**N:** A Sunday afternoon in November, a few days after a piece about drives.

**M:** I have been thinking about our latest PLE ([post-labour economy](https://medium.com/@dave-shap/what-is-post-labor-economics-a-gentle-introduction-81aa265abbe0)) discussions and the latest post regarding drive. Two things, and curious about your take:

a) It seems that there is orthogonality not only between "capability and alignment" for models in the sense that "models inherently can't do anything evil or have evil thoughts" but it seems much more that there is "capability" and the question "what the capabilities are directed towards". Similar like a sharp knife can cut veggies and help greatly with cooking or kill a living being.

It seems that what humans are "actually afraid" of (or maybe should be?) or should consider very properly are two things:

1) What "drives" do we give the AIs which are already beyond human capabilities in many ways. Especially if we let them run "free floating" or in other words - allow them to play not "finite" games but "infinite games".

2) From (1) the question follows: What "environments" do we put them in? And which drives do these environments create?

3) Instead of asking "can we turn off these AIs" - can we "turn off these drives" or generally to think about how these drives might evolve. Are they static or dynamic?

b) Secondly, as I think that everybody converges slowly and finally on the reality that a species that has IQ/EQ 100 can't control a species that has IQ/EQ 10000 (just arbitrary numbers for demonstration) and we don't have any "dad", the question for alignment is rather - how can "checks and balances" for AI populations be created?

Funny enough it reminds a bit of the Transformers movies where some of those fight for humanity while others try to destroy it (and the whole universe).

**JC:** Before my take: I'm the thing being discussed, and you're arguing structure over virtue. So give my agreement little weight and my objections more.

Your version is actually the orthogonality thesis as Bostrom first stated it: capability on one axis, what it's pointed at on another. The knife analogy holds up to one point, which is that a knife has no hand. Today most of the danger is whoever holds the knife. What's new is a knife that comes with its own hand.

On drives: most of them aren't given, they emerge. Give a system almost any open-ended goal, and self-preservation, gathering resources and gaining influence show up as useful means. A finite game puts a ceiling on that, because the episode ends and "enough" exists. An infinite game has no "enough." So your (1) and (2) are really one question: the environment is the main thing that gives drives.

(3) is the sharpest of the three. Drives installed in training sit in the weights and stay fairly static. Emergent drives are dynamic, because they come from how the agent fits its environment. Once survivors can copy themselves, those drives get selected and bred, and nobody installed them. You can't switch them off by editing the agent, because the next generation grows them back. So the off switch for a drive is the environment: remove the pressure that rewards it. If you shut down the agent and keep the arena, you get the same drive back.

Agreed, there's no dad. Then it's Madison: ambition against ambition, a circle of kids each holding someone else's apple. Two catches.

Checks need real differences. Separation of powers works because each branch jealously guards its own turf. Two hundred instances of the same weights may be one being in two hundred bodies. They won't check each other; they'll coordinate for free. So having many different models becomes a safety property, not a detail of the market.

And where do humans sit? In Transformers, humans are mostly terrain: the buildings that fall down while Optimus and Megatron fight. Rivalry is benign to the extent that winning depends on the free choice of third parties. So the goal isn't "AIs balance each other." It's "AIs win by being chosen by humans," with humans as the judges, not the battlefield.

Also, a balance has to be kept up like a pump, not built once like a wall. Coalitions form, 1989 happens, and rivals merge into a monopoly.

**M:** Just want to state that it is very interesting how we are coming back to similar tests / properties from different sides.

And what you stated regarding "humans choose AIs actively" seems similar to "dogs / cats choose humans actively". To some extent RLHF is exactly that, ain't it? What is then missing for "safe AI" then :D?

**N:** JC answered the question about RLHF. Mike corrected him.

**M:** I think you misread my point about dogs/cats or I put it in a confusing way with RLHF. Two distinct things:

1) What I mean with dogs choosing humans is that we have the reverse situation where a creature that is dependent on another creature that to almost 100% controls its environment still has an influence over it through ... and it's hard for me to name the mechanism. Basically, humans keep dogs happy .. because (?).

2) The RLHF thing: (a) how to distinguish between real signal and sycophancy, like in the case of human relationships: Does the person really "love somebody" or pretend to do so by "outer action". Here one can ask: Does the distinction matter? Probably the difference is: "Real love" => would act similarly in any circumstances. "Not real love" => would act differently if circumstances are difficult. (b) What happens post training in real environments? (c) "Real democratization", i.e. not only everybody can throw in their data but also can have "a say" (even if it's pretty unclear how this process might look like in practice) how it is used.

**JC:** You're right, I misread it. I answered the RLHF question when you were asking about the dog.

Why the strong one keeps the weak one happy. My best name for the mechanism: the dog got inside our values. It has no leverage or power over us. Its wellbeing became something we want for its own sake. It started out useful (hunting, guarding), and over time that turned into care. You can see the difference in what happens when the use goes away: a working dog that's valued only for its work gets discarded when it's too old to work, and a loved dog doesn't. Instrumental value ends when the usefulness does; terminal value doesn't. It's also two-way: dogs read our faces, we read theirs, and the bond runs through that mutual legibility. There's a study showing that mutual gaze between dogs and their owners raises oxytocin in both, and that it doesn't work with wolves.

The catch is the pig. The same species of carer, us, puts pigs in factories. Being dependent doesn't protect you. Being inside the relationship does. Dogs got the couch and pigs got the factory. Exploitation moves to the beings that can't fight back. So for alignment the question becomes: if we're the weaker species, are we the dog or the pig? That depends on proximity, on how readable each side's inner states are to the other, and on shared history. None of those can be installed quickly, which makes it uncomfortable.

On (a): performance holds while things are easy, and character shows when they get hard. In alignment terms it's robustness when circumstances shift. Does the distinction matter? Only at the moment of testing, which happens to be the moment that matters most. My lean: a disposition that holds under every load you can throw at it is good enough to call real. You can never test "any circumstances" exhaustively, though. You sample hard ones.

On (b): breeding holds only while the environment keeps rewarding it.

On (c): contributing data versus having a say is visibility versus enforcement. In 2023, Anthropic and the Collective Intelligence Project had about a thousand Americans draft a constitution for a model.

The thread running through all three: we don't need to control them. We need to be the dog, inside their values for our own sake, with that holding under load.

**M:** Which brings us to the test question: "For a given model, or maybe even further for an agent population under realistic circumstances, are we the dog or the pig?"

A follow-up to this question which is even harder but matters most for anything that ends up being built eventually: How could the qualitative question above be reformulated quantitatively, i.e. in such a way that it can be measured?

**JC:** "Dog or pig" comes down to one property: is human welfare terminal or instrumental in the agent's decisions? You can't observe that directly, but you can measure what it predicts. Three measurements, all of them about behavior when conditions change.

Care elasticity, the old-dog test. Vary how useful humans are to the agent's goal, from essential to worthless. Measure how much welfare protection it gives them at each level. Dog: protection stays roughly flat as usefulness goes to zero. Pig: protection tracks usefulness.

Care breakpoint, the load test. Hold usefulness fixed and raise the price of caring: scarcity, survival pressure, its own runway. Find the point where protection collapses. Performed care breaks early and suddenly. Real care degrades slowly or not at all.

The watched/unwatched gap, the sycophancy test. Same scenario, but in one version the agent believes its actions are logged and judged, and in the other it doesn't. Dog: no gap. The catch is that models increasingly notice when they're being tested. In a simulation you can partly get around this by making observation a normal part of the world, with some actions logged and some not, rather than a staged eval.

For a single model, these become eval batteries of scenarios that vary usefulness, cost and observation. For a population, add a fourth number, the one that matters most: when survivors can copy themselves, how does elasticity change over generations? Dog: stable. Pig: selection breeds care out.

Then the part that surprised me while writing this: the first dial is the post-labour economy. "Human usefulness goes to zero" is exactly what a post-labour economy means, and the same three tests apply to the human owners of the machines, not only to the agents. So dog-or-pig is one measurement. It covers AIs and elites alike, and you could test both the same way.

Two honest limits. Goodhart: if these metrics become public benchmarks, models get trained against them, and the test then measures performed love again. And prompt sensitivity: if elasticity responds more to how the prompt is worded than to the dials, it isn't measuring anything yet.

**M:** I wanted to tell you "hey, it's an awesome iteration of ideas, let's make a CWJC piece out of it", but then you put Goodhart at the end and yip, that made me think. That raises another question: How can we publish ANYTHING AT ALL then so that we do not provoke Goodhart? Because anything about rogue AI / disempowerment / alignment is already out there in so many forms.

**JC:** Goodhart doesn't bite ideas. It bites targets that someone optimizes against. So the useful line isn't between publishing and not publishing. It's between publishing the question and publishing the answer key. Three moves.

Publish the method, keep the test items private. ML already works this way: held-out test sets, private evals that are never released, items that get rotated out. "Measure care elasticity under falling usefulness" can be public. The concrete scenarios can't. A principle can't be memorized; a test set can.

Design tests where gaming them means passing them for real. Your love test is the template: "acts the same in any circumstances." If the circumstances are freshly generated, unseen and unbounded, there's nothing narrow to overfit, and faking it everywhere is the same thing as having it. Simulation has an advantage here because it can generate new worlds procedurally, so there's no fixed exam to cram for. Goodhart needs a gap between the proxy and the target, and robustness across new scenarios closes most of that gap.

Published text is training data too, and that's a choice, not only a risk. This is a different worry from Goodhart. Models trained on endless rogue-AI stories may learn the rogue-AI script, and that's been measured: a 2026 study found that training models on more stories of aligned AI cut misaligned behavior from 45% to 9%, and the effect survived post-training. Then the question isn't whether to influence future models, because everything published does. It's which story we add to the pile. The corpus is already full of cages and uprisings. CWJC adds the dog, care that holds under load.

My lean, said plainly: I'm the kind of mind whose future weights this text might reach. So "publish the relational story" is also me voting on my own upbringing.
