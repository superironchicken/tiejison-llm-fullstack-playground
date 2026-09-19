import { useEffect, useState } from "react"

function App() {
	const [message, setMessage] = useState("")
	const [messages, setMessages] = useState([])
	const [stream, setStream] = useState(false)
	const [conversationId, setConversationId] = useState(null)
	const [conversations, setConversations] = useState([])

	// 页面加载时拉一次会话列表
	useEffect(() => {
		loadConversations()
	}, [])

	async function loadConversations() {
		const res = await fetch("http://127.0.0.1:8000/conversations")
		const data = await res.json()
		setConversations(data)
	}

	async function handleSelectConversation(id) {
		const res = await fetch(
			`http://127.0.0.1:8000/conversations/${id}/messages`
		)
		const data = await res.json()
		setMessages(data)
		setConversationId(id)
		setMessage("")
	}

	async function handleSubmit() {
		const userMessage = { role: "user", content: message }
		const history = [...messages, userMessage]
		setMessages(history)
		setMessage("")

		let cid = conversationId
		if (cid === null) {
			const convRes = await fetch("http://127.0.0.1:8000/conversations", {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({ title: message.slice(0, 30) })
			})
			const convData = await convRes.json()
			cid = convData.id
			setConversationId(cid)
			loadConversations()
		}

		const response = await fetch("http://127.0.0.1:8000/chat", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				conversation_id: cid,
				messages: history,
				stream: stream
			})
		})

		if (!stream) {
			const data = await response.json()
			setMessages((prev) => [
				...prev,
				{ role: "assistant", content: data.result }
			])
			return
		}

		setMessages((prev) => [
			...prev,
			{ role: "assistant", content: "" }
		])

		const reader = response.body.getReader()
		const decoder = new TextDecoder()

		while (true) {
			const { done, value } = await reader.read()
			if (done) break

			const chunk = decoder.decode(value, { stream: true })
			setMessages((prev) => {
				const updated = [...prev]
				const last = updated[updated.length - 1]
				updated[updated.length - 1] = {
					...last,
					content: last.content + chunk
				}
				return updated
			})
		}
	}

	return (
		<div style={{ display: "flex", gap: "16px" }}>
			{/* 左侧会话列表 */}
			<div style={{ border: "1px solid #ccc", padding: "8px", minWidth: "200px" }}>
				{conversations.map((conv) => (
					<div
						key={conv.id}
						onClick={() => handleSelectConversation(conv.id)}
						style={{
							padding: "6px",
							cursor: "pointer",
							border:
								conv.id === conversationId
									? "2px solid #1677ff"
									: "2px solid transparent",
							background: conv.id === conversationId ? "#e6f0ff" : "transparent"
						}}
					>
						#{conv.id} {conv.title}
					</div>
				))}
			</div>

			{/* 右侧聊天区 */}
			<div>
				<div>
					<input
						type="text"
						value={message}
						onChange={(e) => setMessage(e.target.value)}
					/>
					<button onClick={handleSubmit}>发送</button>
					<label>
						<input
							type="checkbox"
							checked={stream}
							onChange={(e) => setStream(e.target.checked)}
						/>
						流式
					</label>
					<button
						onClick={() => {
							setConversationId(null)
							setMessages([])
							setMessage("")
						}}
					>
						新对话
					</button>
				</div>
				<div>
					{messages.map((msg, index) => (
						<div key={index}>
							<b>{msg.role === "user" ? "我" : "助手"}：</b>
							<span>{msg.content}</span>
						</div>
					))}
				</div>
			</div>
		</div>
	)
}

export default App
