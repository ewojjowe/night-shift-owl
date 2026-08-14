"""The curriculum, ported verbatim from the original HTML page.

In ``Night-Shift-Learning-Roadmap.html`` this data lived as JavaScript arrays
(``MATH``, ``DSA``, ``PYTHON``, ...) plus a ``TRACKS`` metadata map. Here it is the
exact same content expressed as typed ``Track`` objects, so it can be seeded into
MongoDB once and then served from the database.

Nothing in this file talks to the database — it is pure data. The seeder in
``seed.py`` is what actually writes ``build_curriculum()`` into the collection.
"""

from app.models.curriculum import Lesson, Resource, Track


def _r(name: str, url: str) -> Resource:
    """Tiny constructor mirroring the page's ``R(name, url)`` helper.

    It exists only to keep the lesson definitions below compact and readable —
    ``_r("Khan Academy", "https://...")`` reads better than spelling out the model.
    """
    return Resource(name=name, url=url)


# --- MATH (daily) ----------------------------------------------------------
_MATH = [
    Lesson(t="Arithmetic Foundations Review", f="Order of operations, integers, decimals, mental math speed", res=[_r("Khan Academy — Arithmetic", "https://www.khanacademy.org/math/arithmetic"), _r("Paul's Online Math Notes — Algebra Prep", "https://tutorial.math.lamar.edu/"), _r("Brilliant — Number Theory Warmups", "https://brilliant.org/")]),
    Lesson(t="Fractions & Ratios", f="Fraction arithmetic, simplifying, ratios & proportions", res=[_r("Khan Academy — Fractions", "https://www.khanacademy.org/math/arithmetic/fraction-arithmetic"), _r("Math is Fun — Fractions", "https://www.mathsisfun.com/fractions.html")]),
    Lesson(t="Exponents & Roots", f="Exponent rules, radicals, scientific notation", res=[_r("Khan Academy — Exponents", "https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:exponent-equations"), _r("Math is Fun — Exponents", "https://www.mathsisfun.com/exponent.html")]),
    Lesson(t="Algebra I — Linear Equations", f="Solving for x, rearranging formulas", res=[_r("Khan Academy — Algebra I", "https://www.khanacademy.org/math/algebra"), _r("Paul's Online Notes — Algebra", "https://tutorial.math.lamar.edu/Classes/Alg/Alg.aspx")]),
    Lesson(t="Algebra II — Systems & Inequalities", f="Systems of equations, inequalities, graphing lines", res=[_r("Khan Academy — Systems of Equations", "https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:systems-of-equations")]),
    Lesson(t="Functions — Basics & Notation", f="Domain, range, function notation, composition", res=[_r("Khan Academy — Functions", "https://www.khanacademy.org/math/algebra2/x2ec2f6f830c9fb89:functions"), _r("Professor Leonard (YouTube)", "https://www.youtube.com/@ProfessorLeonard")]),
    Lesson(t="Functions — Graphing & Transformations", f="Shifts, stretches, reflections of graphs", res=[_r("Desmos Graphing Calculator", "https://www.desmos.com/calculator"), _r("Khan Academy — Transformations", "https://www.khanacademy.org/math/algebra2")]),
    Lesson(t="Logarithms & Exponential Functions", f="Log rules, exponential growth/decay", res=[_r("Khan Academy — Logarithms", "https://www.khanacademy.org/math/algebra2/x2ec2f6f830c9fb89:logs"), _r("Math is Fun — Logarithms", "https://www.mathsisfun.com/algebra/logarithms.html")]),
    Lesson(t="Trigonometry — Unit Circle & Ratios", f="Sin, cos, tan, the unit circle", res=[_r("Khan Academy — Trigonometry", "https://www.khanacademy.org/math/trigonometry"), _r("Paul's Online Notes — Trig", "https://tutorial.math.lamar.edu/Classes/Alg/Trig.aspx")]),
    Lesson(t="Trigonometry — Identities & Applications", f="Identities, triangle applications", res=[_r("Khan Academy — Trig Identities", "https://www.khanacademy.org/math/trigonometry/trig-equations-and-identities")]),
    Lesson(t="Probability — Fundamentals", f="Counting, independent/dependent events", res=[_r("Khan Academy — Probability", "https://www.khanacademy.org/math/statistics-probability/probability-library"), _r("Brilliant — Probability", "https://brilliant.org/courses/probability-fundamentals/")]),
    Lesson(t="Probability — Distributions", f="Binomial, normal distribution basics", res=[_r("Khan Academy — Statistics & Probability", "https://www.khanacademy.org/math/statistics-probability")]),
    Lesson(t="Discrete Math — Logic & Sets", f="Propositional logic, set theory", res=[_r("MIT OCW 6.042J — Math for CS", "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/")]),
    Lesson(t="Discrete Math — Combinatorics", f="Permutations, combinations, counting principles", res=[_r("MIT OCW 6.042J", "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/"), _r("Brilliant — Combinatorics", "https://brilliant.org/courses/combinatorics/")]),
    Lesson(t="Discrete Math — Graph Theory Basics", f="Graphs, trees, basic proofs — feeds directly into DSA graphs", res=[_r("MIT OCW 6.042J — Graph Theory unit", "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/"), _r("Brilliant — Graph Theory", "https://brilliant.org/courses/graph-theory/")]),
    Lesson(t="Linear Algebra — Vectors", f="Vectors, dot product, geometric intuition", res=[_r("3Blue1Brown — Essence of Linear Algebra", "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"), _r("Khan Academy — Linear Algebra", "https://www.khanacademy.org/math/linear-algebra")]),
    Lesson(t="Linear Algebra — Matrices & Operations", f="Matrix multiplication, transformations", res=[_r("3Blue1Brown — Linear Algebra series", "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"), _r("MIT 18.06 (Gilbert Strang)", "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/")]),
    Lesson(t="Linear Algebra — Determinants & Inverses", f="Determinants, inverse matrices, solving systems", res=[_r("MIT 18.06", "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/")]),
    Lesson(t="Linear Algebra — Eigenvalues & Eigenvectors", f="Eigen-decomposition — core to PCA & ML later", res=[_r("3Blue1Brown — Eigenvectors & Eigenvalues", "https://www.youtube.com/watch?v=PFDu9oVAE-g"), _r("MIT 18.06", "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/")]),
    Lesson(t="Calculus — Limits, Derivatives & Gradients", f="Derivatives, the gradient — what backpropagation actually uses", res=[_r("3Blue1Brown — Essence of Calculus", "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr"), _r("MIT 18.01 Single Variable Calculus", "https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/")]),
]

# --- DSA (daily) -----------------------------------------------------------
_DSA = [
    Lesson(t="Arrays", f="Traversal, in-place edits, prefix sums", res=[_r("NeetCode — Arrays", "https://neetcode.io/"), _r("LeetCode — Array tag", "https://leetcode.com/tag/array/")]),
    Lesson(t="Strings", f="Pattern scanning, parsing, string builders", res=[_r("LeetCode — String tag", "https://leetcode.com/tag/string/"), _r("NeetCode — Strings", "https://neetcode.io/")]),
    Lesson(t="Hash Maps", f="Lookup tricks, frequency counting", res=[_r("LeetCode — Hash Table tag", "https://leetcode.com/tag/hash-table/"), _r("NeetCode — Hashing", "https://neetcode.io/")]),
    Lesson(t="Linked Lists", f="Reversal, fast/slow pointers, cycle detection", res=[_r("LeetCode — Linked List tag", "https://leetcode.com/tag/linked-list/"), _r("NeetCode — Linked List playlist", "https://neetcode.io/")]),
    Lesson(t="Stacks", f="Monotonic stacks, matching/parsing problems", res=[_r("LeetCode — Stack tag", "https://leetcode.com/tag/stack/")]),
    Lesson(t="Queues", f="FIFO structures, deque, sliding-window uses", res=[_r("GeeksforGeeks — Queue Data Structure", "https://www.geeksforgeeks.org/queue-data-structure/"), _r("LeetCode — Queue tag", "https://leetcode.com/tag/queue/")]),
    Lesson(t="Trees (Binary Trees)", f="Traversals — inorder, preorder, postorder", res=[_r("LeetCode — Tree tag", "https://leetcode.com/tag/tree/"), _r("NeetCode — Trees playlist", "https://neetcode.io/")]),
    Lesson(t="Binary Search Trees", f="BST invariants, insert/delete/search", res=[_r("GeeksforGeeks — BST", "https://www.geeksforgeeks.org/binary-search-tree-data-structure/"), _r("LeetCode — Binary Search Tree tag", "https://leetcode.com/tag/binary-search-tree/")]),
    Lesson(t="Heaps / Priority Queues", f="Min/max heaps, top-k problems", res=[_r("LeetCode — Heap (Priority Queue) tag", "https://leetcode.com/tag/heap-priority-queue/"), _r("NeetCode — Heap", "https://neetcode.io/")]),
    Lesson(t="Graphs — Representation", f="Adjacency list/matrix, weighted vs unweighted", res=[_r("NeetCode — Graphs", "https://neetcode.io/"), _r("LeetCode — Graph tag", "https://leetcode.com/tag/graph/")]),
    Lesson(t="DFS", f="Recursive & iterative depth-first search", res=[_r("NeetCode — DFS", "https://neetcode.io/"), _r("LeetCode — Depth-First Search tag", "https://leetcode.com/tag/depth-first-search/")]),
    Lesson(t="BFS", f="Level-order traversal, shortest path on unweighted graphs", res=[_r("NeetCode — BFS", "https://neetcode.io/"), _r("LeetCode — Breadth-First Search tag", "https://leetcode.com/tag/breadth-first-search/")]),
    Lesson(t="Dynamic Programming — Basics", f="Memoization, tabulation, classic 1D DP", res=[_r("NeetCode — Dynamic Programming playlist", "https://neetcode.io/"), _r("LeetCode — Dynamic Programming tag", "https://leetcode.com/tag/dynamic-programming/")]),
    Lesson(t="Dynamic Programming — Advanced", f="2D DP, interval DP, DP on trees", res=[_r("Educative — Grokking Dynamic Programming Patterns", "https://www.educative.io/courses/grokking-dynamic-programming-patterns-for-coding-interviews"), _r("LeetCode — DP tag", "https://leetcode.com/tag/dynamic-programming/")]),
    Lesson(t="Greedy Algorithms", f="Interval scheduling, greedy proofs", res=[_r("LeetCode — Greedy tag", "https://leetcode.com/tag/greedy/"), _r("GeeksforGeeks — Greedy Algorithms", "https://www.geeksforgeeks.org/greedy-algorithms/")]),
    Lesson(t="Backtracking", f="Combinations, permutations, constraint search", res=[_r("NeetCode — Backtracking", "https://neetcode.io/"), _r("LeetCode — Backtracking tag", "https://leetcode.com/tag/backtracking/")]),
    Lesson(t="Tries & Union-Find", f="Prefix trees, disjoint-set union for connectivity", res=[_r("LeetCode — Trie tag", "https://leetcode.com/tag/trie/"), _r("LeetCode — Union Find tag", "https://leetcode.com/tag/union-find/")]),
    Lesson(t="Mixed Review & Mock Interviews", f="Timed practice across all patterns", res=[_r("NeetCode 150 list", "https://neetcode.io/practice"), _r("Pramp — free mock interviews", "https://www.pramp.com/")]),
]

# --- PYTHON (Monday) -------------------------------------------------------
_PYTHON = [
    Lesson(t="Advanced Syntax", f="Comprehensions, generators, iterators", res=[_r("Real Python — List/Dict Comprehensions", "https://realpython.com/list-comprehension-python/"), _r("Real Python — Iterators & Iterables", "https://realpython.com/python-for-loop/"), _r("Python docs — Functional Programming HOWTO", "https://docs.python.org/3/howto/functional.html")]),
    Lesson(t="OOP", f="Classes, inheritance, dunder methods", res=[_r("Python docs — Classes", "https://docs.python.org/3/tutorial/classes.html"), _r("Real Python — OOP in Python 3", "https://realpython.com/python3-object-oriented-programming/")]),
    Lesson(t="Typing", f="Type hints, mypy, Protocol", res=[_r("Python docs — typing module", "https://docs.python.org/3/library/typing.html"), _r("Real Python — Python Type Checking Guide", "https://realpython.com/python-type-checking/")]),
    Lesson(t="Decorators", f="Function wrapping, functools.wraps, parameterized decorators", res=[_r("Real Python — Primer on Python Decorators", "https://realpython.com/primer-on-python-decorators/")]),
    Lesson(t="Context Managers", f="The with statement, contextlib", res=[_r("Real Python — Context Managers", "https://realpython.com/python-with-statement/"), _r("Python docs — contextlib", "https://docs.python.org/3/library/contextlib.html")]),
    Lesson(t="Async / Await", f="Coroutines, event loop, asyncio", res=[_r("Real Python — Async IO in Python", "https://realpython.com/async-io-python/"), _r("Python docs — asyncio", "https://docs.python.org/3/library/asyncio.html")]),
    Lesson(t="Multiprocessing & Concurrency", f="Threads vs processes, the GIL", res=[_r("Python docs — multiprocessing", "https://docs.python.org/3/library/multiprocessing.html"), _r("Real Python — Speed Up Python with Concurrency", "https://realpython.com/python-concurrency/")]),
    Lesson(t="Networking", f="Sockets, HTTP clients", res=[_r("Python docs — socket", "https://docs.python.org/3/library/socket.html"), _r("Real Python — Python's Requests library", "https://realpython.com/python-requests/")]),
    Lesson(t="Flask / FastAPI", f="Building a web API", res=[_r("FastAPI — official docs", "https://fastapi.tiangolo.com/"), _r("Flask — official docs", "https://flask.palletsprojects.com/")]),
    Lesson(t="SQLAlchemy / Databases", f="ORMs, migrations, queries", res=[_r("SQLAlchemy — official docs", "https://docs.sqlalchemy.org/"), _r("Real Python — SQLAlchemy ORM Tutorial", "https://realpython.com/python-sqlite-sqlalchemy/")]),
    Lesson(t="Testing", f="pytest, fixtures, mocking", res=[_r("pytest — official docs", "https://docs.pytest.org/"), _r("Real Python — Getting Started With Testing", "https://realpython.com/python-testing/")]),
    Lesson(t="Performance & Profiling", f="cProfile, timeit, optimization", res=[_r("Python docs — cProfile", "https://docs.python.org/3/library/profile.html"), _r("Real Python — Python Profiling", "https://realpython.com/python-profiling/")]),
    Lesson(t="Design Patterns", f="Classic OOP patterns in a Python idiom", res=[_r("Refactoring.Guru — Design Patterns (Python)", "https://refactoring.guru/design-patterns/python"), _r("python-patterns.guide", "https://python-patterns.guide/")]),
    Lesson(t="Production Python", f="Packaging, logging, deployment", res=[_r("Python Packaging User Guide", "https://packaging.python.org/"), _r("Real Python — Logging in Python", "https://realpython.com/python-logging/")]),
]

# --- GO (Wednesday) --------------------------------------------------------
_GO = [
    Lesson(t="Language Basics Review", f="Syntax, types, control flow", res=[_r("A Tour of Go", "https://go.dev/tour/"), _r("Effective Go", "https://go.dev/doc/effective_go")]),
    Lesson(t="Structs & Methods", f="Value vs pointer receivers", res=[_r("Go by Example — Structs", "https://gobyexample.com/structs"), _r("Go by Example — Methods", "https://gobyexample.com/methods")]),
    Lesson(t="Interfaces", f="Implicit interfaces, composition over inheritance", res=[_r("Go by Example — Interfaces", "https://gobyexample.com/interfaces"), _r("Effective Go — Interfaces", "https://go.dev/doc/effective_go#interfaces")]),
    Lesson(t="Error Handling", f="Error values, wrapping, custom errors", res=[_r("Go blog — Error handling and Go", "https://go.dev/blog/error-handling-and-go"), _r("Go by Example — Errors", "https://gobyexample.com/errors")]),
    Lesson(t="Goroutines", f="Lightweight concurrency", res=[_r("Go by Example — Goroutines", "https://gobyexample.com/goroutines"), _r("A Tour of Go — Concurrency", "https://go.dev/tour/concurrency/1")]),
    Lesson(t="Channels", f="Communicating between goroutines, select", res=[_r("Go by Example — Channels", "https://gobyexample.com/channels"), _r("A Tour of Go — Channels", "https://go.dev/tour/concurrency/2")]),
    Lesson(t="Context Package", f="Cancellation, timeouts, request-scoped values", res=[_r("pkg.go.dev — context", "https://pkg.go.dev/context"), _r("Go blog — Context", "https://go.dev/blog/context")]),
    Lesson(t="HTTP Servers", f="net/http, routing, middleware", res=[_r("Go by Example — HTTP Servers", "https://gobyexample.com/http-servers"), _r("pkg.go.dev — net/http", "https://pkg.go.dev/net/http")]),
    Lesson(t="Database Integration", f="database/sql, GORM", res=[_r("pkg.go.dev — database/sql", "https://pkg.go.dev/database/sql"), _r("GORM — official docs", "https://gorm.io/docs/")]),
    Lesson(t="Testing in Go", f="table-driven tests, benchmarks", res=[_r("pkg.go.dev — testing", "https://pkg.go.dev/testing"), _r("Go by Example — Testing and Benchmarking", "https://gobyexample.com/testing-and-benchmarking")]),
    Lesson(t="Microservices Patterns", f="Service boundaries, gRPC basics", res=[_r("grpc-go — official docs", "https://grpc.io/docs/languages/go/"), _r("Go blog", "https://go.dev/blog/")]),
    Lesson(t="Production Go", f="Profiling, observability, deployment", res=[_r("pkg.go.dev — pprof", "https://pkg.go.dev/net/http/pprof"), _r("Prometheus Go client library", "https://github.com/prometheus/client_golang")]),
]

# --- AI / ML (Tuesday) -----------------------------------------------------
_AIML = [
    Lesson(t="Math Refresher for ML", f="Connecting linear algebra & calculus to ML", res=[_r("3Blue1Brown — Essence of Linear Algebra", "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"), _r("StatQuest (YouTube)", "https://www.youtube.com/@statquest")]),
    Lesson(t="NumPy", f="Arrays, broadcasting, vectorized ops", res=[_r("NumPy — official quickstart", "https://numpy.org/doc/stable/user/quickstart.html")]),
    Lesson(t="Pandas", f="DataFrames, cleaning, groupby", res=[_r("pandas — Getting Started guide", "https://pandas.pydata.org/docs/getting_started/index.html")]),
    Lesson(t="Data Visualization", f="Matplotlib & Seaborn basics", res=[_r("Matplotlib — tutorials", "https://matplotlib.org/stable/tutorials/index.html"), _r("Seaborn — official docs", "https://seaborn.pydata.org/")]),
    Lesson(t="Statistics for ML", f="Mean/variance, hypothesis testing, correlation", res=[_r("StatQuest (YouTube)", "https://www.youtube.com/@statquest"), _r("Khan Academy — Statistics", "https://www.khanacademy.org/math/statistics-probability")]),
    Lesson(t="Linear & Logistic Regression", f="Your first predictive models", res=[_r("scikit-learn — Linear Models", "https://scikit-learn.org/stable/modules/linear_model.html"), _r("StatQuest — Regression playlist", "https://www.youtube.com/@statquest")]),
    Lesson(t="Classification & Ensembles", f="kNN, decision trees, random forests", res=[_r("scikit-learn — Supervised Learning", "https://scikit-learn.org/stable/supervised_learning.html"), _r("StatQuest — Random Forests", "https://www.youtube.com/@statquest")]),
    Lesson(t="Neural Network Fundamentals", f="Perceptrons, backprop intuition", res=[_r("3Blue1Brown — Neural Networks series", "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi"), _r("Michael Nielsen — Neural Networks and Deep Learning (free book)", "http://neuralnetworksanddeeplearning.com/")]),
    Lesson(t="PyTorch Basics", f="Tensors, autograd, a first training loop", res=[_r("PyTorch — official tutorials", "https://pytorch.org/tutorials/")]),
    Lesson(t="Transformer Architecture", f="Attention — the bridge into AI Engineering", res=[_r("Jay Alammar — The Illustrated Transformer", "https://jalammar.github.io/illustrated-transformer/"), _r("Hugging Face — NLP Course", "https://huggingface.co/learn/nlp-course")]),
]

# --- AI ENGINEERING (Friday) -----------------------------------------------
_AIENG = [
    Lesson(t="LLM Fundamentals", f="How large language models work at a high level", res=[_r("Hugging Face — LLM Course", "https://huggingface.co/learn"), _r("OpenAI — Docs overview", "https://platform.openai.com/docs")]),
    Lesson(t="Prompt Engineering", f="Structuring prompts for reliable output", res=[_r("Claude — Prompt Engineering Guide", "https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview"), _r("OpenAI — Prompt Engineering guide", "https://platform.openai.com/docs/guides/prompt-engineering")]),
    Lesson(t="Embeddings", f="Turning text into vectors for search & similarity", res=[_r("Pinecone Learning Center — Embeddings", "https://www.pinecone.io/learn/vector-embeddings/"), _r("OpenAI — Embeddings guide", "https://platform.openai.com/docs/guides/embeddings")]),
    Lesson(t="Vector Databases", f="Indexing & querying embeddings at scale", res=[_r("Pinecone Learning Center", "https://www.pinecone.io/learn/"), _r("Chroma — docs", "https://docs.trychroma.com/")]),
    Lesson(t="RAG Basics", f="Retrieval-Augmented Generation fundamentals", res=[_r("Pinecone Learning Center — RAG", "https://www.pinecone.io/learn/retrieval-augmented-generation/"), _r("LangChain — RAG docs", "https://python.langchain.com/docs/tutorials/rag/")]),
    Lesson(t="Advanced RAG", f="Chunking strategies, hybrid search, reranking", res=[_r("LlamaIndex — docs", "https://docs.llamaindex.io/"), _r("LangChain — docs", "https://python.langchain.com/")]),
    Lesson(t="AI Agents — Basics", f="Tool use, planning loops", res=[_r("LangChain — Agents docs", "https://python.langchain.com/docs/concepts/agents/"), _r("Anthropic — Building effective agents", "https://www.anthropic.com/research/building-effective-agents")]),
    Lesson(t="Multi-Agent Systems & Tool Use", f="Coordinating multiple agents, MCP", res=[_r("Model Context Protocol — docs", "https://modelcontextprotocol.io/"), _r("LangGraph — docs", "https://langchain-ai.github.io/langgraph/")]),
    Lesson(t="Fine-tuning & Evaluation", f="When and how to fine-tune, measuring quality", res=[_r("OpenAI — Fine-tuning guide", "https://platform.openai.com/docs/guides/fine-tuning"), _r("Hugging Face — Fine-tuning tutorial", "https://huggingface.co/docs/transformers/training")]),
    Lesson(t="Production AI / LLMOps", f="Monitoring, cost, evals in production", res=[_r("Weights & Biases — LLMOps resources", "https://wandb.ai/site/llmops/"), _r("Claude — API docs", "https://docs.claude.com/")]),
]

# --- SYSTEM DESIGN (Thursday) ----------------------------------------------
_SYSDESIGN = [
    Lesson(t="Single Server Design & Fundamentals", f="Where every system design starts", res=[_r("System Design Primer (GitHub)", "https://github.com/donnemartin/system-design-primer")]),
    Lesson(t="Databases", f="SQL vs NoSQL, indexing, normalization", res=[_r("System Design Primer — Database section", "https://github.com/donnemartin/system-design-primer#database")]),
    Lesson(t="Caching Fundamentals", f="Cache-aside, write-through, eviction policies", res=[_r("System Design Primer — Caching", "https://github.com/donnemartin/system-design-primer#cache")]),
    Lesson(t="Redis Deep Dive", f="Data structures, expiry, pub/sub", res=[_r("Redis — official docs", "https://redis.io/docs/latest/")]),
    Lesson(t="Message Queues", f="Decoupling producers & consumers", res=[_r("System Design Primer — Message Queues", "https://github.com/donnemartin/system-design-primer#asynchronism"), _r("RabbitMQ — docs", "https://www.rabbitmq.com/docs")]),
    Lesson(t="Scaling", f="Vertical vs horizontal scaling", res=[_r("System Design Primer — Scalability", "https://github.com/donnemartin/system-design-primer#scalability")]),
    Lesson(t="Load Balancers", f="Algorithms, health checks, L4 vs L7", res=[_r("System Design Primer — Load Balancer", "https://github.com/donnemartin/system-design-primer#load-balancer"), _r("NGINX — docs", "https://nginx.org/en/docs/")]),
    Lesson(t="Microservices Architecture", f="Service boundaries, trade-offs", res=[_r("Martin Fowler — Microservices", "https://martinfowler.com/articles/microservices.html")]),
    Lesson(t="Event-Driven Architecture", f="Pub/sub, event sourcing", res=[_r("Martin Fowler — Event-Driven Architecture", "https://martinfowler.com/articles/201701-event-driven.html"), _r("Confluent — Event-driven guide", "https://www.confluent.io/learn/event-driven-architecture/")]),
    Lesson(t="Kafka & Streaming", f="Topics, partitions, consumer groups", res=[_r("Apache Kafka — official docs", "https://kafka.apache.org/documentation/")]),
    Lesson(t="Observability", f="Logging, metrics, tracing", res=[_r("Grafana — docs", "https://grafana.com/docs/"), _r("Prometheus — docs", "https://prometheus.io/docs/introduction/overview/")]),
    Lesson(t="Distributed Systems Concepts", f="CAP theorem, consensus, replication", res=[_r("MIT 6.824 — Distributed Systems", "https://pdos.csail.mit.edu/6.824/")]),
    Lesson(t="Cloud Architecture", f="Reference architectures on AWS/GCP", res=[_r("AWS — Well-Architected Framework", "https://aws.amazon.com/architecture/well-architected/"), _r("Google Cloud — Architecture Center", "https://cloud.google.com/architecture")]),
    Lesson(t="Production-Grade Design & Mock Interviews", f="Whiteboard practice on real case studies", res=[_r("ByteByteGo (YouTube)", "https://www.youtube.com/@ByteByteGo"), _r("System Design Primer — Interview prep", "https://github.com/donnemartin/system-design-primer#system-design-interview-questions-with-solutions")]),
]

# --- PROJECTS (Sunday) — no resources, just title + focus ------------------
_PROJECTS = [
    Lesson(t="CLI Tool in Python", f="Practice OOP + typing in a real, small tool"),
    Lesson(t="REST API in Go", f="net/http + a database — your first Go service"),
    Lesson(t="Python AI Service", f="FastAPI wrapping a scikit-learn model"),
    Lesson(t="Dockerize Your Go API", f="Containerize what you built in week 2"),
    Lesson(t="Add a Redis Caching Layer", f="Bolt caching onto an existing API"),
    Lesson(t="Queue-Based Worker", f="RabbitMQ/Kafka powering an async job"),
    Lesson(t="RAG Chatbot Over Your Own Docs", f="Python + a vector DB, end to end"),
    Lesson(t="Kubernetes Deployment", f="Deploy your dockerized services to a cluster"),
    Lesson(t="CI/CD Pipeline", f="GitHub Actions for your Go/Python services"),
    Lesson(t="Tool-Using AI Agent", f="An agent that calls real tools via MCP"),
    Lesson(t="Full-Stack Capstone", f="API + caching + queue + RAG + auth, combined"),
    Lesson(t="Open-Source Contribution", f="Ship a real PR to a Go or Python project"),
]


def build_curriculum() -> list[Track]:
    """Assemble every track (plus the projects list) as ``Track`` documents.

    The metadata here — label, weekday, icon, kind — is the exact ``TRACKS`` map
    from the HTML, so the seeded database reproduces the original app faithfully.
    ``key`` values must match ``TRACK_KEYS`` in ``models/progress.py`` so a user's
    per-track progress counters line up with the curriculum they describe.
    """
    return [
        Track(key="math", label="Math", day="Daily", icon="∑", kind="track", lessons=_MATH),
        Track(key="dsa", label="DSA", day="Daily", icon="⌥", kind="track", lessons=_DSA),
        Track(key="python", label="Python", day="Monday", icon="🐍", kind="track", lessons=_PYTHON),
        Track(key="aiml", label="AI / ML", day="Tuesday", icon="📊", kind="track", lessons=_AIML),
        Track(key="go", label="Go", day="Wednesday", icon="🐹", kind="track", lessons=_GO),
        Track(key="sysdesign", label="System Design", day="Thursday", icon="🏗", kind="track", lessons=_SYSDESIGN),
        Track(key="aieng", label="AI Engineering", day="Friday", icon="✨", kind="track", lessons=_AIENG),
        Track(key="projects", label="Projects", day="Sunday", icon="🛠", kind="projects", lessons=_PROJECTS),
    ]
