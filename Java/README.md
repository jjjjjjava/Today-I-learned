## Java知识体系框架

### 1. **基础语法**

- **变量与数据类型**：基本数据类型（如 `int`, `char`, `double` 等）和引用类型（如 `Object`, `String`, `Array`）。
- **运算符**：算术、关系、逻辑、位运算符等。
- **流程控制**：条件语句（`if-else`，`switch`），循环（`for`，`while`，`do-while`），异常处理（`try-catch-finally`）。
- **方法与参数传递**：方法的定义与调用，参数传递（值传递与引用传递），可变参数。

### 2. **面向对象编程（OOP）**

- **类与对象**：类的定义、实例化对象、构造方法、对象的生命周期。
- **封装、继承、多态**：封装（`private`, `protected`, `public`），继承（`extends`），多态（方法的重载与重写，动态绑定）。
- **抽象类与接口**：抽象类（`abstract`），接口（`interface`），接口与抽象类的区别与使用场景。
- **内部类与匿名类**：成员内部类、局部内部类、匿名内部类的使用与场景。
- **枚举**：枚举类型 `enum` 的定义和使用。

### 3. **Java 集合框架（Java Collections Framework, JCF）**

- **List、Set、Map、Queue**：`ArrayList`, `LinkedList`, `HashSet`, `TreeSet`, `HashMap`, `TreeMap`, `PriorityQueue` 等集合类的特点与使用场景。
- **集合的遍历**：使用 `Iterator`，`for-each` 循环，`Stream` API 进行集合的遍历与操作。
- **集合工具类**：`Collections` 和 `Arrays` 工具类提供的常用方法，如排序、搜索、修改等。

### 4. **异常处理**

- **异常类型**：`Checked` 和 `Unchecked` 异常，常见的异常类如 `Exception`, `RuntimeException`, `IOException`, `NullPointerException` 等。
- **自定义异常**：如何定义和抛出自定义异常。
- **异常处理机制**：`try-catch-finally` 块的使用，异常的传播，`throws` 声明。

### 5. **多线程与并发编程**

- **线程基础**：`Thread` 类与 `Runnable` 接口，线程的生命周期（新建、运行、阻塞、终止）。
- **同步机制**：`synchronized` 关键字、锁对象、死锁、线程通信（`wait`, `notify`）。
- **线程池**：`ExecutorService`, `ThreadPoolExecutor`，如何使用线程池管理并发任务。
- **并发工具类**：`CountDownLatch`, `CyclicBarrier`, `Semaphore`, `Future`, `Callable`, `ForkJoinPool` 等并发工具。
- **Java 内存模型（JMM）**：可见性、原子性、有序性，`volatile`, `final`, `happens-before` 原则。
- **锁机制**：`ReentrantLock`, `ReadWriteLock`, `StampedLock`，`synchronized` 与 `Lock` 的比较。

### 6. **输入输出（IO）与 NIO**

- **IO 流**：字节流（`InputStream`, `OutputStream`），字符流（`Reader`, `Writer`），缓冲流，数据流，对象流等。
- **文件操作**：`File` 类的使用，文件的读写，目录操作。
- **序列化与反序列化**：如何实现 `Serializable` 接口，`ObjectInputStream` 和 `ObjectOutputStream` 的使用。
- **NIO（New IO）**：`Buffer`, `Channel`, `Selector`，非阻塞 IO 的概念和应用场景。

### 7. **JVM（Java Virtual Machine）**

- **JVM 内存模型**：堆（Heap），方法区（Method Area），栈（Stack），本地方法栈（Native Method Stack），程序计数器（Program Counter）。
- **类加载机制**：类加载过程（加载、验证、准备、解析、初始化），`ClassLoader`。
- **垃圾回收机制**：垃圾回收算法（标记-清除，标记-整理，复制算法），垃圾回收器（Serial, Parallel, CMS, G1），如何调优 GC。
- **JVM 参数调优**：常见的 JVM 启动参数，如何进行性能监控和调优（`-Xmx`, `-Xms`, `-XX:+UseG1GC` 等）。

### 8. **Java 8 及以后的新特性**

- **Lambda 表达式**：简化匿名内部类的写法，函数式编程的引入。
- **Stream API**：处理集合的高级操作，包括过滤、映射、聚合等。
- **默认方法与静态接口方法**：接口中的默认实现方法和静态方法。
- **Optional 类**：避免 `NullPointerException` 的实用工具类。
- **新时间日期 API**：`LocalDate`, `LocalTime`, `ZonedDateTime`，取代 `Date` 和 `Calendar`。

### 9. **泛型与反射**

- **泛型**：泛型类、泛型方法，类型擦除，`<? extends T>` 和 `<? super T>` 的使用场景。
- **反射**：`Class` 对象，`Method`，`Field`，`Constructor` 的反射操作，如何通过反射调用方法、访问字段和构造对象。
- **注解与动态代理**：如何定义和使用自定义注解，动态代理的实现原理与应用。

### 10. **网络编程**

- **Socket 编程**：基于 TCP 和 UDP 的通信，`Socket` 和 `ServerSocket` 的使用。
- **HTTP 请求处理**：使用 `HttpURLConnection`，第三方库如 `OkHttp`, `Apache HttpClient`。
- **NIO 及 Netty**：使用 NIO 的 `Selector`、`Channel` 实现高效的网络通信，Netty 框架的介绍与应用。

### 11. **数据库操作**

- **JDBC**：如何使用 JDBC 连接数据库，执行 SQL 语句，处理结果集。
- **ORM 框架**：使用 Hibernate、MyBatis 等持久化框架，掌握其配置、映射、查询等操作。

### 12. **Java 企业开发（Java EE）**

- **Servlet 和 JSP**：如何构建 Java Web 应用，Servlet 的生命周期，JSP 的基础。
- **Spring 框架**：Spring 的核心概念（依赖注入，AOP），Spring MVC，Spring Boot，Spring Cloud 的应用场景。
- **Java EE 规范**：EJB（企业级 Java Bean）、JPA（Java 持久化 API），Web 服务（RESTful 与 SOAP）。

### 13. **工具与开发实践**

- **Maven/Gradle**：构建管理工具，项目依赖管理，生命周期管理。
- **版本控制**：Git 的基本命令与使用，如何使用 Git 管理项目版本。
- **单元测试**：JUnit, Mockito 的使用，如何编写有效的单元测试。
- **代码质量与静态分析**：如何使用 SonarQube、PMD、FindBugs 等工具分析代码质量。