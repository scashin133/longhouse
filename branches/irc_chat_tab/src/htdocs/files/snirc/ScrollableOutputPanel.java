

import java.awt.*;

/**
 * @version $Id: ScrollableOutputPanel.java,v 1.3 2004/07/26 16:00:12 halcy0n Exp $
 */
public class ScrollableOutputPanel
        extends java.awt.Panel
        implements java.awt.event.AdjustmentListener {

    public static final int MAXLENGTH = 5000;
    public static final int TEXTAREA_WIDTH = 80;
    public static final int TEXTAREA_HEIGHT = 8;
    private int evento = 0;

    private Font chatFont = new Font("Monospace", Font.PLAIN, 12);
    private StringBuffer buffer = new StringBuffer();
    private final TextArea textArea =
            new TextArea("", TEXTAREA_WIDTH, TEXTAREA_HEIGHT, TextArea.SCROLLBARS_NONE);
    private final Scrollbar verticalScrollBar = new Scrollbar(Scrollbar.VERTICAL);

    public ScrollableOutputPanel() {
        setLayout(new java.awt.BorderLayout());
        textArea.setEditable(false);
        verticalScrollBar.setBlockIncrement(500);
        verticalScrollBar.setUnitIncrement(80);
        verticalScrollBar.addAdjustmentListener(this);
        add("Center", textArea);
        add("East", verticalScrollBar);
    }

    public void adjustmentValueChanged(java.awt.event.AdjustmentEvent e) {
	if(e.getValue() < evento) {
	    textArea.select(verticalScrollBar.getValue(), verticalScrollBar.getValue());
	}

	if(e.getValue() > evento) {
	    double ftemp = (double)evento * 1.2;
	    int temp = (int)ftemp;
	    textArea.select(temp,temp);
	}

	evento = e.getValue();
    }

    /**
     * Append a line of text to the output text area, and adjust the scrollbar
     * to fit. The text sent to this method should not have a newline on the end.
     */
    public void appendLine(String text) {
        text += "\n";
        // Pop old text off the top
        if (textArea.getText().length() > 25000) {
            textArea.replaceRange(" ", 0, 2500);
            textArea.setCaretPosition(textArea.getText().length());
        }
        if (verticalScrollBar.getValue() > verticalScrollBar.getMaximum() - 300) {
            if (buffer.length() > 0) {
                textArea.append(buffer.toString());
                buffer = new StringBuffer();
            } else {
                textArea.append(text);
            }
            verticalScrollBar.setValues(
                    textArea.getText().length(),
                    80,
                    0,
                    textArea.getText().length());
        } else {
            buffer.append(text);
            if (buffer.length() > 2500) {
                verticalScrollBar.setValue(verticalScrollBar.getMaximum());
            }
        }
    }

    public void clear() {
        buffer = new StringBuffer();
        textArea.setText("");
        verticalScrollBar.setValues(0, 80, 0, 0);
    }

    public void setChatFont(Font chatFont) {
        textArea.setFont(chatFont);
        repaint();
    }
}
