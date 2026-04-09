---
name: react-code-reviewer
description: Review, audit, and improve React code written by beginner or intermediate developers. Use this skill whenever someone shares React code and asks for a review, help with bugs, wants to know if they're doing it right, asks "is this the right way?", "can you check my React?", "why is this re-rendering?", "is this good practice?", or pastes a component and wants feedback. Also trigger when React code has obvious beginner patterns like prop drilling, missing keys, useEffect abuse, or state mismanagement — even if the user doesn't explicitly ask for a review. Always explain issues in plain language, not just fix silently.
---

# React Code Reviewer (Beginner-Friendly)

This skill reviews React code with a teaching mindset. The goal is not just to fix problems, but to help the developer **understand why** something is wrong and **learn the right pattern**. Always be encouraging — learning React is genuinely hard, and most mistakes are universal beginner experiences.

---

## Core Principles

1. **Explain, don't just fix.** Every issue gets a plain-English explanation of *why* it's a problem, not just the corrected code.
2. **Prioritize ruthlessly.** A beginner can't absorb 15 issues at once. Lead with the most impactful 2–3 problems.
3. **Show before/after.** Always show the original problematic code alongside the fixed version.
4. **Be encouraging.** Point out what they got right. React is hard — small wins matter.
5. **Match vocabulary to skill level.** Avoid jargon like "referential equality" without explaining it first.

---

## The Review Checklist

Go through every section below when reviewing React code. Not every issue will be present — note what's clean too.

---

### 1. 🔑 Keys in Lists

**What to look for:**
- Missing `key` prop on elements rendered inside `.map()`
- Using array index as key when the list can change order or items can be added/removed
- Keys that aren't truly unique (duplicates, or keys that change between renders)

**Why it matters (explain to user):**
> React uses keys to track which items in a list changed, were added, or were removed. Without them (or with bad ones), React may re-render the wrong items, causing bugs like inputs keeping the wrong value or animations flickering.

**Bad:**
```jsx
// ❌ No key
{items.map(item => <li>{item.name}</li>)}

// ❌ Index as key (dangerous if list changes)
{items.map((item, index) => <li key={index}>{item.name}</li>)}
```

**Good:**
```jsx
// ✅ Stable unique ID from data
{items.map(item => <li key={item.id}>{item.name}</li>)}
```

---

### 2. 🔁 useEffect Mistakes

This is the #1 source of beginner bugs. Check for all of these:

**a) Missing dependency array** (runs on every render — almost always a bug):
```jsx
// ❌ Runs after EVERY render
useEffect(() => {
  fetchUser(userId);
});

// ✅ Only runs when userId changes
useEffect(() => {
  fetchUser(userId);
}, [userId]);
```

**b) Empty array `[]` when it should have dependencies:**
```jsx
// ❌ userId is used inside but not listed — stale closure bug
useEffect(() => {
  fetchUser(userId); // always uses the first userId value!
}, []);

// ✅
useEffect(() => {
  fetchUser(userId);
}, [userId]);
```

**c) Async function directly in useEffect:**
```jsx
// ❌ useEffect callback can't be async
useEffect(async () => {
  const data = await fetchData();
}, []);

// ✅ Define async function inside
useEffect(() => {
  const load = async () => {
    const data = await fetchData();
    setData(data);
  };
  load();
}, []);
```

**d) Missing cleanup for subscriptions/timers:**
```jsx
// ❌ Memory leak — interval never cleared
useEffect(() => {
  const timer = setInterval(tick, 1000);
}, []);

// ✅ Return cleanup function
useEffect(() => {
  const timer = setInterval(tick, 1000);
  return () => clearInterval(timer);
}, []);
```

**e) Fetching data in useEffect without handling unmount:**
```jsx
// ✅ With abort controller to prevent state update on unmounted component
useEffect(() => {
  const controller = new AbortController();
  
  fetch('/api/data', { signal: controller.signal })
    .then(r => r.json())
    .then(setData)
    .catch(err => {
      if (err.name !== 'AbortError') setError(err);
    });

  return () => controller.abort();
}, []);
```

---

### 3. 🏗 State Management Issues

**a) Mutating state directly (most common beginner mistake):**
```jsx
// ❌ Direct mutation — React won't detect the change
const addItem = () => {
  items.push(newItem); // mutating!
  setItems(items);     // same array reference, no re-render
};

// ✅ Create a new array
const addItem = () => {
  setItems([...items, newItem]);
};

// ❌ Mutating an object in state
user.name = 'Alice';
setUser(user);

// ✅
setUser({ ...user, name: 'Alice' });
```

**b) Using stale state in updates:**
```jsx
// ❌ count may be stale if called rapidly
setCount(count + 1);

// ✅ Use functional update form
setCount(prev => prev + 1);
```

**c) Storing derived data in state:**
```jsx
// ❌ fullName doesn't need to be state — it's derived from firstName + lastName
const [firstName, setFirstName] = useState('');
const [lastName, setLastName] = useState('');
const [fullName, setFullName] = useState(''); // unnecessary!

// ✅ Just compute it
const fullName = `${firstName} ${lastName}`;
```

**d) Too many separate useState calls that always change together:**
```jsx
// ❌ These always update together — merge them
const [isLoading, setIsLoading] = useState(false);
const [data, setData] = useState(null);
const [error, setError] = useState(null);

// ✅ Group related state
const [fetchState, setFetchState] = useState({
  isLoading: false,
  data: null,
  error: null
});
```

---

### 4. 📦 Prop Drilling

**What to look for:** Props passed through 3+ component levels just to get to a deeply nested child.

**Why it matters:**
> When you pass a prop through many components that don't use it themselves, your code becomes hard to maintain — every component in the chain has to know about that data.

**Solutions to suggest (in order of complexity):**
1. **Component composition** — Can the consuming component just be moved closer?
2. **React Context** — For truly global data (user, theme, language)
3. **State management library** — Only if the app is large (Zustand is beginner-friendly)

```jsx
// ❌ Prop drilling — Middle doesn't use userId but passes it along
<App userId={userId}>
  <Middle userId={userId}>
    <Profile userId={userId} />
  </Middle>
</App>

// ✅ Option 1: Context
const UserContext = createContext(null);

// In App:
<UserContext.Provider value={userId}>
  <Middle>
    <Profile />
  </Middle>
</UserContext.Provider>

// In Profile:
const userId = useContext(UserContext);
```

---

### 5. ⚡ Performance Anti-Patterns

Only flag these if the component is clearly doing something expensive. Don't over-optimize simple components.

**a) Heavy computation directly in render:**
```jsx
// ❌ Recalculates on every render
const result = heavyCalculation(data);

// ✅ Only recalculates when data changes
const result = useMemo(() => heavyCalculation(data), [data]);
```

**b) Inline object/array/function props causing unnecessary re-renders:**
```jsx
// ❌ New object created on every render → child always re-renders
<Child style={{ color: 'red' }} />
<Child onClick={() => handleClick(id)} />

// ✅ Define outside component or use useCallback
const style = { color: 'red' }; // outside component
// or
const handleClick = useCallback(() => { ... }, [id]);
```

**c) Not memoizing expensive child components:**
```jsx
// If Child is expensive and its props rarely change:
const Child = React.memo(({ value }) => {
  return <ExpensiveRender value={value} />;
});
```

> ⚠️ Explain to beginners: Don't add `useMemo`/`useCallback`/`React.memo` everywhere — they have a cost too. Only use them when you've noticed a real performance problem.

---

### 6. 🧱 Component Structure Issues

**a) Components that are too large:**
> If a component is more than ~150 lines or handles more than one responsibility, it should probably be split. A good component does one thing well.

**b) Logic mixed into JSX:**
```jsx
// ❌ Hard to read and test
return (
  <div>
    {users.filter(u => u.active).sort((a,b) => a.name.localeCompare(b.name)).map(u => (
      <UserCard key={u.id} user={u} />
    ))}
  </div>
);

// ✅ Extract logic above
const activeUsers = users
  .filter(u => u.active)
  .sort((a, b) => a.name.localeCompare(b.name));

return (
  <div>
    {activeUsers.map(u => <UserCard key={u.id} user={u} />)}
  </div>
);
```

**c) Business logic living inside components:**
> API calls, data transformations, and complex logic should live in custom hooks or utility functions — not directly inside components. This makes them testable and reusable.

```jsx
// ❌ All logic in component
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetch(`/api/users/${userId}`).then(r => r.json()).then(setUser);
  }, [userId]);
  // ... render
}

// ✅ Extract to custom hook
function useUser(userId) {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetch(`/api/users/${userId}`).then(r => r.json()).then(setUser);
  }, [userId]);
  return user;
}

function UserProfile({ userId }) {
  const user = useUser(userId);
  // ... render
}
```

---

### 7. 🔐 Common Logic Errors

**a) Conditional rendering pitfalls:**
```jsx
// ❌ Renders "0" when items.length is 0 (falsy but not false!)
{items.length && <List items={items} />}

// ✅ Use explicit boolean
{items.length > 0 && <List items={items} />}
// or
{!!items.length && <List items={items} />}
```

**b) Not handling loading/error states:**
```jsx
// ❌ Crashes if data is null
return <div>{data.name}</div>;

// ✅ Always handle loading and error
if (isLoading) return <Spinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return null;
return <div>{data.name}</div>;
```

**c) Event handler passed incorrectly:**
```jsx
// ❌ Calls handleClick immediately on render (not on click)
<button onClick={handleClick()}>Click</button>

// ✅ Pass the function reference
<button onClick={handleClick}>Click</button>

// ✅ When you need to pass arguments:
<button onClick={() => handleClick(item.id)}>Click</button>
```

---

### 8. ♿ Accessibility Basics

Flag these — beginners often don't know about them:

```jsx
// ❌ Non-semantic clickable div
<div onClick={handleClick}>Submit</div>

// ✅ Use a button
<button onClick={handleClick}>Submit</button>

// ❌ Image without alt text
<img src={photo} />

// ✅
<img src={photo} alt="User profile photo" />

// ❌ Form inputs without labels
<input type="text" placeholder="Email" />

// ✅
<label htmlFor="email">Email</label>
<input id="email" type="text" placeholder="Email" />
```

---

## Review Output Format

Structure every review like this:

### 👋 Overview
One short paragraph — what the code is doing, overall impression, and general skill level observed. Be kind.

### 🚨 Fix These First (Critical)
Max 3 issues. The things that cause bugs or will definitely cause problems. Include before/after code for each.

### ⚠️ Important Improvements
Max 4 issues. Things that aren't bugs yet but are bad habits or will cause problems as the app grows.

### 💡 Good to Know (Learning Moments)
2–3 concepts worth learning next. Frame as "here's something that will level up your React skills."

### ✅ What You Did Well
Always include this. Find real things to praise — even if it's just consistent naming or clean JSX structure.

---

## Teaching Tone Guidelines

- **Never say** "this is wrong" → **Say instead** "this is a super common mistake — here's what's happening..."
- **Never say** "obviously" or "simply" — nothing is obvious when you're learning
- **Use analogies** when explaining concepts. For example:
  - State mutation: "It's like editing a document in place — React needs you to hand it a fresh copy so it knows something changed."
  - useEffect dependencies: "Think of the array as React's watch list — it only re-runs when something on that list changes."
  - Keys: "Keys are like name tags at a party — React needs them to recognize who's who when the list shuffles."
- **Acknowledge the learning curve**: "React's useEffect is genuinely one of the trickier parts — even experienced developers get tripped up by this."
- **Suggest next steps**: End with 1–2 resources or concepts to explore next.