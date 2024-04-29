#include "TaskQueue.h"

namespace misc {

bool Task::operator ()(std::unique_lock<std::mutex>& lk)
{
	size_t n = m_pending;
	lk.unlock();
	m_task();
	lk.lock();
	m_pending -= n;
	return m_pending == 0;
}

TaskQueue::TaskQueue()
	: m_head(NULL)
	, m_tail(NULL)
	, m_shutdown(false)
{
}

TaskQueue::~TaskQueue()
{
	shutdown();
}

void TaskQueue::enqueue(Task& task)
{
	std::lock_guard<std::mutex> lk(m_mtx);
	if (task.incrPending() > 1)
		return;
	pushTask(&task);
	m_cv.notify_one();
}

void TaskQueue::drain(Task& task)
{
	std::unique_lock<std::mutex> lk(m_mtx);
	task.setDraining();
	while (task.isPending())
		m_cv.wait(lk);
	task.setDraining(false);
}

bool TaskQueue::run(bool block)
{
	std::unique_lock<std::mutex> lk(m_mtx);
	while (true) {
		if (m_shutdown)
			return false;
		if (Task* task = popTask()) {
			bool complete = (*task)(lk);
			if (complete) {
				if (task->isDraining())
					m_cv.notify_all();
			}
			else
				pushTask(task);
			continue;
		}
		if (!block)
			break;
		m_cv.wait(lk);
	}
	return true;
}

void TaskQueue::shutdown()
{
	std::lock_guard<std::mutex> lk(m_mtx);
	m_shutdown = true;
	m_cv.notify_all();
}

} // namespace misc
