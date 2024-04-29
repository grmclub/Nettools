#ifndef MISC_TASKQUEUE_H
#define MISC_TASKQUEUE_H

#include <condition_variable>
#include <cstddef>
#include <functional>
#include <mutex>
#include <utility>

namespace misc {

class Task
{
public:
	friend class TaskQueue;

	Task(const Task&) = delete;
	Task& operator =(const Task&) = delete;

	template <typename Callable, typename... Args>
	explicit Task(Callable f, Args&&... args)
		: m_task(std::bind(f, std::forward<Args>(args)...))
		, m_pending(0)
		, m_draining(false)
		, m_next(NULL)
	{
	}

private:
	std::function<void ()> m_task;
	size_t m_pending;
	bool m_draining;
	Task* m_next;

	bool operator ()(std::unique_lock<std::mutex>&);

	size_t incrPending()
	{
		return ++m_pending;
	}

	bool isPending() const
	{
		return m_pending > 0;
	}

	void setDraining(bool flag = true)
	{
		m_draining = flag;
	}

	bool isDraining() const
	{
		return m_draining;
	}
};

class TaskQueue
{
public:
	TaskQueue(const TaskQueue&) = delete;
	TaskQueue& operator =(const TaskQueue&) = delete;

	TaskQueue();

	~TaskQueue();

	void enqueue(Task&);

	void drain(Task&);

	bool run(bool);

	void shutdown();

private:
	Task* m_head;
	Task* m_tail;
	std::mutex m_mtx;
	std::condition_variable m_cv;
	bool m_shutdown;

	void pushTask(Task* task)
	{
		if (m_tail != NULL)
			m_tail->m_next = task;
		else
			m_head = task;
		m_tail = task;
	}

	Task* popTask()
	{
		Task* task = m_head;
		if (task != NULL) {
			m_head = task->m_next;
			if (m_head != NULL)
				task->m_next = NULL;
			else
				m_tail = NULL;
		}
		return task;
	}
};

} // namespace misc

#endif // MISC_TASKQUEUE_H
