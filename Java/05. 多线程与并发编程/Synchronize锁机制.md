[toc]

## 01.Synchronize介绍

### 什么是Synchronize

Synchronize分时期，早期的底层就是内核互斥锁，当然，内核互斥锁其实就是带着等待队列的M类型Semaphore，即互斥信号量。信号量有很多种类，还有C类型计数信号量等等。当其尝试获取锁时，就是尝试对全局的某个互斥信号量循环判断是否是1，如果超时，那么其会被阻塞在等待队列中，当其它线程释放锁，让互斥信号量为1时会到等待队列中进行调度，唤醒被阻塞的线程。

Synchronize在现在是三种类型：偏向锁（无锁）-	轻量化锁（自旋锁）-	重量级锁（也就是上面的内核互斥锁）其中偏向锁和轻量化锁无需进行线程的阻塞睡眠和唤醒切换。非常节省时间。

### 它的作用是什么

实现多线程并发的三要素。



## 02.Synchronize用法

它看起来应用场景很多，但是实际上概括下来，它可以修饰两种，一个是类的实例对象。一个是类的class对象。

修饰代码块，普通方法，就是修饰类的实例对象，在该对象内执行会互斥。修饰静态方法和一个类，或者使用.class结尾，就是修饰类的class对象，在类的所有对象中执行都会互斥。。



## 03.理解Synchronize锁机制

### Monitor锁机制

`synchronized` 的实现机制依赖于 JVM 中的 **Monitor**（监视器）。在 JVM（如 HotSpot）中，Monitor 由 C++ 实现，具体由 **ObjectMonitor** 类来表示。每个 Java 对象都有一个与之关联的 Monitor。

Monitor 有一个**计数器**，表示当前锁的状态：

- 当线程第一次获得锁时，计数器从 0 变为 1。
- 如果同一个线程再次获得锁（可重入锁的特性），计数器继续增加。
- 当线程执行完同步代码块并释放锁时，计数器递减。当计数器降到 0 时，锁释放，其他线程可以尝试获取锁。

`ObjectMonitor` 提供了以下关键方法来实现同步的基本操作：

- **enter**：线程尝试获取 Monitor，成功则进入同步代码块，失败则进入同步队列等待。
- **exit**：线程释放 Monitor，计数器递减。如果计数器为 0，则锁释放。
- **wait**：线程在同步块中调用 `wait()` 方法时，会释放 Monitor，并进入等待队列，直到被 `notify()` 或 `notifyAll()` 唤醒。
- **notify**：唤醒等待队列中的一个线程。
- **notifyAll**：唤醒等待队列中的所有线程。

### Synchronized 的字节码实现

当使用 `synchronized` 关键字时，JVM 会在编译后的字节码中生成两条指令：

- **`monitorenter`**：进入同步块，尝试获取锁。
- **`monitorexit`**：退出同步块，释放锁。

每个对象都有一个与之关联的 **Monitor**（监视器），当线程执行 `monitorenter` 指令时，它会尝试获取该对象的 Monitor，如果获取成功则进入同步代码块，否则线程将被阻塞。

### 代码块同步和方法同步的区别

对于使用 `synchronized` 关键字的**同步代码块**，JVM 会插入 `monitorenter` 和 `monitorexit` 字节码指令.并通过其完成对对象的monitor的获取和释放。

当 `synchronized` 用于**同步方法**时，JVM 在方法的 `method_info` 结构中标记该方法为 **ACC_SYNCHRONIZED**。此时JVM 在调用方法时自动获取对象的 `Monitor`，在方法执行完毕后自动释放 `Monitor`，不需要显式的 `monitorenter` 和 `monitorexit` 指令。

举例：

- 我们有如下反编译代码：

  ```
  public synchronized void doSth();
      descriptor: ()V
      flags: ACC_PUBLIC, ACC_SYNCHRONIZED
      Code:
        stack=2, locals=1, args_size=1
           0: getstatic     #2                  // Field java/lang/System.out:Ljava/io/PrintStream;
           3: ldc           #3                  // String Hello World
           5: invokevirtual #4                  // Method java/io/PrintStream.println:(Ljava/lang/String;)V
           8: return
  
  public void doSth1();
      descriptor: ()V
      flags: ACC_PUBLIC
      Code:
        stack=2, locals=3, args_size=1
           0: ldc           #5                  // class com/hollis/SynchronizedTest
           2: dup
           3: astore_1
           4: monitorenter
           5: getstatic     #2                  // Field java/lang/System.out:Ljava/io/PrintStream;
           8: ldc           #3                  // String Hello World
          10: invokevirtual #4                  // Method java/io/PrintStream.println:(Ljava/lang/String;)V
          13: aload_1
          14: monitorexit
          15: goto          23
          18: astore_2
          19: aload_1
          20: monitorexit
          21: aload_2
          22: athrow
          23: return
  ```

  

- 通过反编译后代码可以看出：

  - 对于同步方法，JVM采用`ACC_SYNCHRONIZED`标记符来实现同步。
  - 对于同步代码块，JVM采用`monitorenter`、`monitorexit`两个指令来实现同步。

## 04. Synchronize与三要素

### 4.1 synchronized与原子性

**原子性**是指一个操作是不可分割的，要么全部执行成功，要么不执行。

synchronized能实现原子性有两个重要的因素，一个是其字节码指令 `monitorenter` 和 `monitorexit`是原子操作，也就是其获取锁时是原子操作，其获取锁要么完全成功，要么被阻塞失败，不会有其它结果。另一个是因为执行 `monitorenter`获取到锁后，它将进入临界区，执行代码块，此时执行过程是原子性的，不会被破坏。

### 4.2 synchronized与可见性

- 可见性是指当多个线程访问同一个变量时，一个线程修改了这个变量的值，其他线程能够立即看得到修改的值。
- Java内存模型规定了所有的变量都存储在主内存中，每条线程还有自己的工作内存，线程的工作内存中保存了该线程中是用到的变量的主内存副本拷贝，线程对变量的所有操作都必须在工作内存中进行，而不能直接读写主内存。不同的线程之间也无法直接访问对方工作内存中的变量，线程间变量的传递均需要自己的工作内存和主存之间进行数据同步进行。所以，就可能出现线程1改了某个变量的值，但是线程2不可见的情况。
- 前面我们介绍过，被`synchronized`修饰的代码，在开始执行时会加锁，执行完成后会进行解锁。而为了保证可见性，有一条规则是这样的：对一个变量解锁之前，必须先把此变量同步回主存中。这样解锁后，后续线程就可以访问到被修改后的值。
- 所以，synchronized关键字锁住的对象，其值是具有可见性的。

###  4.3 synchronized与有序性

- 有序性即程序执行的顺序按照代码的先后顺序执行，单个线程内部不存在有序性问题。详见什么是多线程并发
  - 这里需要注意的是，`synchronized`是无法禁止指令重排和处理器优化的。也就是说，`synchronized`无法避免上述提到的问题。
- 那么，为什么还说synchronized也提供了有序性保证呢？
  - 这就要再把有序性的概念扩展一下了。Java程序中天然的有序性可以总结为一句话：如果在本线程内观察，所有操作都是天然有序的。如果在一个线程中观察另一个线程，所有操作都是无序的。
- 所以synchronized不是通过禁止指令重排实现有序性，而是保证只有一个线程执行临界区的代码，进而实现其对外部线程的有序性。



## 05.synchronized与锁优化